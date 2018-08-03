# -*- coding: utf-8 -*-
'''
Network Config
==============

Manage the configuration on a network device given a specific static config or template.

:codeauthor: Mircea Ulinic <mircea@cloudflare.com> & Jerome Fleury <jf@cloudflare.com>
:maturity:   new
:depends:    napalm
:platform:   unix

Dependencies
------------
- :mod:`NAPALM proxy minion <salt.proxy.napalm>`
- :mod:`Network-related basic features execution module <salt.modules.napalm_network>`

.. versionadded:: 2017.7.0
'''

# Import Salt libs
from __future__ import absolute_import, print_function, unicode_literals
import logging

log = logging.getLogger(__name__)

# import Salt libs
import salt.utils.napalm

# ----------------------------------------------------------------------------------------------------------------------
# state properties
# ----------------------------------------------------------------------------------------------------------------------

__virtualname__ = 'netconfig'

# ----------------------------------------------------------------------------------------------------------------------
# global variables
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# property functions
# ----------------------------------------------------------------------------------------------------------------------


def __virtual__():
    '''
    NAPALM library must be installed for this module to work and run in a (proxy) minion.
    '''
    return salt.utils.napalm.virtual(__opts__, __virtualname__, __file__)

# ----------------------------------------------------------------------------------------------------------------------
# helper functions -- will not be exported
# ----------------------------------------------------------------------------------------------------------------------


def _update_config(template_name,
                   template_source=None,
                   template_hash=None,
                   template_hash_name=None,
                   template_user='root',
                   template_group='root',
                   template_mode='755',
                   template_attrs='--------------e----',
                   saltenv=None,
                   template_engine='jinja',
                   skip_verify=False,
                   defaults=None,
                   test=False,
                   commit=True,
                   debug=False,
                   replace=False,
                   **template_vars):
    '''
    Call the necessary functions in order to execute the state.
    For the moment this only calls the ``net.load_template`` function from the
    :mod:`Network-related basic features execution module <salt.modules.napalm_network>`, but this may change in time.
    '''

    return __salt__['net.load_template'](template_name,
                                         template_source=template_source,
                                         template_hash=template_hash,
                                         template_hash_name=template_hash_name,
                                         template_user=template_user,
                                         template_group=template_group,
                                         template_mode=template_mode,
                                         template_attrs=template_attrs,
                                         saltenv=saltenv,
                                         template_engine=template_engine,
                                         skip_verify=skip_verify,
                                         defaults=defaults,
                                         test=test,
                                         commit=commit,
                                         debug=debug,
                                         replace=replace,
                                         **template_vars)

# ----------------------------------------------------------------------------------------------------------------------
# callable functions
# ----------------------------------------------------------------------------------------------------------------------


def managed(name,
            template_name,
            template_source=None,
            template_hash=None,
            template_hash_name=None,
            template_user='root',
            template_group='root',
            template_mode='755',
            template_attrs='--------------e----',
            saltenv=None,
            template_engine='jinja',
            skip_verify=False,
            defaults=None,
            test=False,
            commit=True,
            debug=False,
            replace=False,
            commit_in=None,
            commit_at=None,
            revert_in=None,
            revert_at=None,
            **template_vars):

    '''
    Manages the configuration on network devices.

    By default this state will commit the changes on the device. If there are no changes required, it does not commit
    and the field ``already_configured`` from the output dictionary will be set as ``True`` to notify that.

    To avoid committing the configuration, set the argument ``test`` to ``True`` (or via the CLI argument ``test=True``)
    and will discard (dry run).

    To preserve the changes, set ``commit`` to ``False`` (either as CLI argument, either as state parameter).
    However, this is recommended to be used only in exceptional cases when there are applied few consecutive states
    and/or configuration changes. Otherwise the user might forget that the config DB is locked and the candidate config
    buffer is not cleared/merged in the running config.

    To replace the config, set ``replace`` to ``True``. This option is recommended to be used with caution!

    template_name
        Identifies path to the template source. The template can be either stored on the local machine,
        either remotely.
        The recommended location is under the ``file_roots`` as specified in the master config file.
        For example, let's suppose the ``file_roots`` is configured as:

        .. code-block:: yaml

            file_roots:
              base:
                 - /etc/salt/states

        Placing the template under ``/etc/salt/states/templates/example.jinja``, it can be used as
        ``salt://templates/example.jinja``.
        Alternatively, for local files, the user can specify the absolute path.
        If remotely, the source can be retrieved via ``http``, ``https`` or ``ftp``.

        Examples:

        - ``salt://my_template.jinja``
        - ``/absolute/path/to/my_template.jinja``
        - ``http://example.com/template.cheetah``
        - ``https:/example.com/template.mako``
        - ``ftp://example.com/template.py``

    template_source: None
        Inline config template to be rendered and loaded on the device.

    template_hash: None
        Hash of the template file. Format: ``{hash_type: 'md5', 'hsum': <md5sum>}``

    template_hash_name: None
        When ``template_hash`` refers to a remote file, this specifies the filename to look for in that file.

    template_group: root
        Owner of file.

    template_user: root
        Group owner of file.

    template_mode: 755
        Permissions of file

    template_attrs: "--------------e----"
        Attributes of file (see `man lsattr`)

        .. versionadded:: 2018.3.0

    saltenv: base
        Specifies the template environment. This will influence the relative imports inside the templates.

    template_engine: jinja
        The following templates engines are supported:

        - :mod:`cheetah<salt.renderers.cheetah>`
        - :mod:`genshi<salt.renderers.genshi>`
        - :mod:`jinja<salt.renderers.jinja>`
        - :mod:`mako<salt.renderers.mako>`
        - :mod:`py<salt.renderers.py>`
        - :mod:`wempy<salt.renderers.wempy>`

    skip_verify: False
        If ``True``, hash verification of remote file sources (``http://``, ``https://``, ``ftp://``) will be skipped,
        and the ``source_hash`` argument will be ignored.

        .. versionchanged:: 2017.7.1

    test: False
        Dry run? If set to ``True``, will apply the config, discard and return the changes. Default: ``False``
        (will commit the changes on the device).

    commit: True
        Commit? Default: ``True``.

    debug: False
        Debug mode. Will insert a new key under the output dictionary, as ``loaded_config`` containing the raw
        result after the template was rendered.

        .. note::
            This argument cannot be used directly on the command line. Instead,
            it can be passed through the ``pillar`` variable when executing
            either of the :py:func:`state.sls <salt.modules.state.sls>` or
            :py:func:`state.apply <salt.modules.state.apply>` (see below for an
            example).

    commit_in: ``None``
        Commit the changes in a specific number of minutes / hours. Example of
        accepted formats: ``5`` (commit in 5 minutes), ``2m`` (commit in 2
        minutes), ``1h`` (commit the changes in 1 hour)`, ``5h30m`` (commit
        the changes in 5 hours and 30 minutes).

        .. note::
            This feature works on any platforms, as it does not rely on the
            native features of the network operating system.

        .. note::
            After the command is executed and the ``diff`` is not satisfactory,
            or for any other reasons you have to discard the commit, you are
            able to do so using the
            :py:func:`net.cancel_commit <salt.modules.napalm_network.cancel_commit>`
            execution function, using the commit ID returned by this function.

        .. warning::
            Using this feature, Salt will load the exact configuration you
            expect, however the diff may change in time (i.e., if an user
            applies a manual configuration change, or a different process or
            command changes the configuration in the meanwhile).

        .. versionadded: Fluorine

    commit_at: ``None``
        Commit the changes at a specific time. Example of accepted formats:
        ``1am`` (will commit the changes at the next 1AM), ``13:20`` (will
        commit at 13:20), ``1:20am``, etc.

        .. note::
            This feature works on any platforms, as it does not rely on the
            native features of the network operating system.

        .. note::
            After the command is executed and the ``diff`` is not satisfactory,
            or for any other reasons you have to discard the commit, you are
            able to do so using the
            :py:func:`net.cancel_commit <salt.modules.napalm_network.cancel_commit>`
            execution function, using the commit ID returned by this function.

        .. warning::
            Using this feature, Salt will load the exact configuration you
            expect, however the diff may change in time (i.e., if an user
            applies a manual configuration change, or a different process or
            command changes the configuration in the meanwhile).

        .. versionadded: Fluorine

    revert_in: ``None``
        Commit and revert the changes in a specific number of minutes / hours.
        Example of accepted formats: ``5`` (revert in 5 minutes), ``2m`` (revert
        in 2 minutes), ``1h`` (revert the changes in 1 hour)`, ``5h30m`` (revert
        the changes in 5 hours and 30 minutes).

        .. note::
            To confirm the commit, and prevent reverting the changes, you will
            have to execute the
            :mod:`net.confirm_commit <salt.modules.napalm_network.confirm_commit>`
            function, using the commit ID returned by this function.

        .. warning::
            This works on any platform, regardless if they have or don't have
            native capabilities to confirming a commit. However, please be
            *very* cautious when using this feature: on Junos (as it is the only
            NAPALM core platform supporting this natively) it executes a commit
            confirmed as you would do from the command line.
            All the other platforms don't have this capability natively,
            therefore the revert is done via Salt. That means, your device needs
            to be reachable at the moment when Salt will attempt to revert your
            changes. Be cautious when pushing configuration changes that would
            prevent you reach the device.

            Similarly, if an user or a different process apply other
            configuration changes in the meanwhile (between the moment you
            commit and till the changes are reverted), these changes would be
            equally reverted, as Salt cannot be aware of them.

        .. versionadded: Fluorine

    revert_at: ``None``
        Commit and revert the changes at a specific time. Example of accepted
        formats: ``1am`` (will commit and revert the changes at the next 1AM),
        ``13:20`` (will commit and revert at 13:20), ``1:20am``, etc.

        .. note::
            To confirm the commit, and prevent reverting the changes, you will
            have to execute the
            :mod:`net.confirm_commit <salt.modules.napalm_network.confirm_commit>`
            function, using the commit ID returned by this function.

        .. warning::
            This works on any platform, regardless if they have or don't have
            native capabilities to confirming a commit. However, please be
            *very* cautious when using this feature: on Junos (as it is the only
            NAPALM core platform supporting this natively) it executes a commit
            confirmed as you would do from the command line.
            All the other platforms don't have this capability natively,
            therefore the revert is done via Salt. That means, your device needs
            to be reachable at the moment when Salt will attempt to revert your
            changes. Be cautious when pushing configuration changes that would
            prevent you reach the device.

            Similarly, if an user or a different process apply other
            configuration changes in the meanwhile (between the moment you
            commit and till the changes are reverted), these changes would be
            equally reverted, as Salt cannot be aware of them.

        .. versionadded: Fluorine

    replace: False
        Load and replace the configuration. Default: ``False`` (will apply load merge).

    defaults: None
        Default variables/context passed to the template.

    template_vars
        Dictionary with the arguments/context to be used when the template is rendered. Do not explicitly specify this
        argument. This represents any other variable that will be sent to the template rendering system. Please
        see an example below! In both ``ntp_peers_example_using_pillar`` and ``ntp_peers_example``, ``peers`` is sent as
        template variable.

    SLS Example (e.g.: under salt://router/config.sls) :

    .. code-block:: yaml

        whole_config_example:
            netconfig.managed:
                - template_name: salt://path/to/complete_config.jinja
                - debug: True
                - replace: True
        bgp_config_example:
            netconfig.managed:
                - template_name: /absolute/path/to/bgp_neighbors.mako
                - template_engine: mako
        prefix_lists_example:
            netconfig.managed:
                - template_name: prefix_lists.cheetah
                - debug: True
                - template_engine: cheetah
        ntp_peers_example:
            netconfig.managed:
                - template_name: http://bit.ly/2gKOj20
                - skip_verify: False
                - debug: True
                - peers:
                    - 192.168.0.1
                    - 192.168.0.1
        ntp_peers_example_using_pillar:
            netconfig.managed:
                - template_name: http://bit.ly/2gKOj20
                - peers: {{ pillar.get('ntp.peers', []) }}

    Usage examples:

    .. code-block:: bash

        $ sudo salt 'juniper.device' state.sls router.config test=True

        $ sudo salt -N all-routers state.sls router.config pillar="{'debug': True}"

    ``router.config`` depends on the location of the SLS file (see above). Running this command, will be executed all
    five steps from above. These examples above are not meant to be used in a production environment, their sole purpose
    is to provide usage examples.

    Output example:

    .. code-block:: bash

        $ sudo salt 'juniper.device' state.sls router.config test=True
        juniper.device:
        ----------
                  ID: ntp_peers_example_using_pillar
            Function: netconfig.managed
              Result: None
             Comment: Testing mode: Configuration discarded.
             Started: 12:01:40.744535
            Duration: 8755.788 ms
             Changes:
                      ----------
                      diff:
                          [edit system ntp]
                               peer 192.168.0.1 { ... }
                          +    peer 172.17.17.1;
                          +    peer 172.17.17.3;

        Summary for juniper.device
        ------------
        Succeeded: 1 (unchanged=1, changed=1)
        Failed:    0
        ------------
        Total states run:     1
        Total run time:   8.756 s

    Raw output example (useful when the output is reused in other states/execution modules):

    .. code-block:: bash

        $ sudo salt --out=pprint 'juniper.device' state.sls router.config test=True debug=True

    .. code-block:: python

        {
            'juniper.device': {
                'netconfig_|-ntp_peers_example_using_pillar_|-ntp_peers_example_using_pillar_|-managed': {
                    '__id__': 'ntp_peers_example_using_pillar',
                    '__run_num__': 0,
                    'already_configured': False,
                    'changes': {
                        'diff': '[edit system ntp]   peer 192.168.0.1 { ... }+   peer 172.17.17.1;+   peer 172.17.17.3;'
                    },
                    'comment': 'Testing mode: Configuration discarded.',
                    'duration': 7400.759,
                    'loaded_config': 'system {  ntp {  peer 172.17.17.1;  peer 172.17.17.3; } }',
                    'name': 'ntp_peers_example_using_pillar',
                    'result': None,
                    'start_time': '12:09:09.811445'
                }
            }
        }
    '''
    ret = salt.utils.napalm.default_ret(name)

    # the user can override the flags the equivalent CLI args
    # which have higher precedence
    test = __salt__['config.merge']('test', test)
    debug = __salt__['config.merge']('debug', debug)
    commit = __salt__['config.merge']('commit', commit)
    replace = __salt__['config.merge']('replace', replace)  # this might be a bit risky
    skip_verify = __salt__['config.merge']('skip_verify', skip_verify)
    commit_in = __salt__['config.merge']('commit_in', commit_in)
    commit_at = __salt__['config.merge']('commit_at', commit_at)
    revert_in = __salt__['config.merge']('revert_in', revert_in)
    revert_at = __salt__['config.merge']('revert_at', revert_at)

    config_update_ret = _update_config(template_name,
                                       template_source=template_source,
                                       template_hash=template_hash,
                                       template_hash_name=template_hash_name,
                                       template_user=template_user,
                                       template_group=template_group,
                                       template_mode=template_mode,
                                       template_attrs=template_attrs,
                                       saltenv=saltenv,
                                       template_engine=template_engine,
                                       skip_verify=skip_verify,
                                       defaults=defaults,
                                       test=test,
                                       commit=commit,
                                       commit_in=commit_in,
                                       commit_at=commit_at,
                                       revert_in=revert_in,
                                       revert_at=revert_at,
                                       debug=debug,
                                       replace=replace,
                                       **template_vars)

    return salt.utils.napalm.loaded_ret(ret, config_update_ret, test, debug)


def commit_cancelled(name):
    '''
    .. versionadded:: Fluorine

    Cancel a commit scheduled to be executed via the ``commit_in`` and
    ``commit_at`` arguments from the
    :py:func:`net.load_template <salt.modules.napalm_network.load_template>` or
    :py:func:`net.load_config <salt.modules.napalm_network.load_config`
    execution functions. The commit ID is displayed when the commit is scheduled
    via the functions named above.

    State SLS Example:

    .. code-block:: yaml

        20180726083540640360:
          netconfig.commit_cancelled
    '''
    cancelled = {
        'result': None,
        'changes': {},
        'comment': ''
    }
    if __opts__['test']:
        cancelled['comment'] = 'It would cancel commit #{}'.format(name)
        return cancelled
    cancelled = __salt__['net.cancel_commit'](name)
    cancelled['changes'] = {}
    return cancelled


def commit_confirmed(name):
    '''
    .. versionadded:: Fluorine

    Confirm a commit scheduled to be reverted via the ``revert_in`` and
    ``revert_at`` arguments from the
    :mod:`net.load_template <salt.modules.napalm_network.load_template>` or
    :mod:`net.load_config <salt.modules.napalm_network.load_config`
    execution functions. The commit ID is displayed when the commit confirmed
    is scheduled via the functions named above.

    State SLS Example:

    .. code-block:: yaml

        20180726083540640360:
          netconfig.commit_confirmed
    '''
    confirmed = {
        'result': None,
        'changes': {},
        'comment': ''
    }
    if __opts__['test']:
        confirmed['comment'] = 'It would confirm commit #{}'.format(name)
        return confirmed
    confirmed = __salt__['net.confirm_commit'](name)
    confirmed['changes'] = {}
    return confirmed
