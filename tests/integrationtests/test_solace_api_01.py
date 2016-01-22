__author__ = 'johlyh'

import unittest2 as unittest
import libsolace.settingsloader as settings
from libsolace.solace import SolaceAPI


class TestSolaceAPI(unittest.TestCase):

    def setUp(self):
        self.solace = SolaceAPI('dev')

    def test_get_memory(self):
        result = self.solace.get_memory()
        self.assertEqual(type(result), list)

    def test_get_queue(self):
        result = self.solace.get_queue('*', '*')
        self.assertEqual(type(result), list)

    def test_list_queues(self):
        result = self.solace.list_queues('*')
        self.assertEqual(type(result), list)

    def test_get_client(self):
        result = self.solace.get_client('*', '*')
        self.assertEqual(type(result), list)

    def test_get_vpn(self):
        result = self.solace.get_vpn('*')
        self.assertEqual(type(result), list)

    def test_list_vpns(self):
        result = self.solace.list_vpns('*')
        self.assertEqual(type(result), list)

    def test_rpc(self):
        result = self.solace.rpc('<rpc semp-version="soltr/5_3"><show><memory></memory></show></rpc>')
        self.assertEqual(type(result), list)

    def test_is_client_username_inuse(self):
        from libsolace import xml2dict

        ###
        ### MOCKDATA (in use)
        ###
        rpc_string_inuse_h1 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client>
        <primary-virtual-router>
          <client>
            <client-address>10.96.16.4:58983</client-address>
            <name>app0028.proxmox.swe1.unibet.com/20198/#00020001</name>
            <type>Primary</type>
            <profile>glassfish</profile>
            <acl-profile>dev_accounting</acl-profile>
            <num-subscriptions>1</num-subscriptions>
            <no-local>false</no-local>
            <eliding-enabled>false</eliding-enabled>
            <eliding-topics>0</eliding-topics>
            <eliding-topics-hwm>0</eliding-topics-hwm>
            <dto-local-priority>1</dto-local-priority>
            <dto-network-priority>1</dto-network-priority>
            <client-id>7727</client-id>
            <message-vpn>ci1_bonus</message-vpn>
            <uptime>2d 4h 43m 50s</uptime>
            <slow-subscriber>false</slow-subscriber>
            <client-username>ci1_bonus</client-username>
            <user>\'gf31\' Computer: \'app0028.proxmox.swe1.unibet.com\' Process ID: 20198</user>
            <description></description>
            <software-version>6.1.0.197</software-version>
            <software-date>2013/06/26 16:18</software-date>
            <platform>Linux-amd64 (Java 1.7.0_45-b18) - JMS SDK</platform>
            <large-message-event-raised>false</large-message-event-raised>
            <message-too-big-event-raised>false</message-too-big-event-raised>
            <parse-error-event-raised>false</parse-error-event-raised>
            <max-eliding-topics-raised>false</max-eliding-topics-raised>
            <total-ingress-flows>3</total-ingress-flows>
            <total-egress-flows>2</total-egress-flows>
            <web-transport-session>N/A</web-transport-session>
          </client>
          <client>
            <client-address>10.96.16.4:58983</client-address>
            <name>app0028.proxmox.swe1.unibet.com/20198/#00020001</name>
            <type>Primary</type>
            <profile>glassfish</profile>
            <acl-profile>dev_accounting</acl-profile>
            <num-subscriptions>1</num-subscriptions>
            <no-local>false</no-local>
            <eliding-enabled>false</eliding-enabled>
            <eliding-topics>0</eliding-topics>
            <eliding-topics-hwm>0</eliding-topics-hwm>
            <dto-local-priority>1</dto-local-priority>
            <dto-network-priority>1</dto-network-priority>
            <client-id>7727</client-id>
            <message-vpn>ci1_bonus</message-vpn>
            <uptime>2d 4h 43m 50s</uptime>
            <slow-subscriber>false</slow-subscriber>
            <client-username>ci1_bonus</client-username>
            <user>\'gf31\' Computer: \'app0028.proxmox.swe1.unibet.com\' Process ID: 20198</user>
            <description></description>
            <software-version>6.1.0.197</software-version>
            <software-date>2013/06/26 16:18</software-date>
            <platform>Linux-amd64 (Java 1.7.0_45-b18) - JMS SDK</platform>
            <large-message-event-raised>false</large-message-event-raised>
            <message-too-big-event-raised>false</message-too-big-event-raised>
            <parse-error-event-raised>false</parse-error-event-raised>
            <max-eliding-topics-raised>false</max-eliding-topics-raised>
            <total-ingress-flows>3</total-ingress-flows>
            <total-egress-flows>2</total-egress-flows>
            <web-transport-session>N/A</web-transport-session>
          </client>
        </primary-virtual-router>
        <internal-virtual-router>
          <client>
            <client-address>127.55.55.55:17</client-address>
            <name>#client</name>
            <type>Internal</type>
            <profile>#client-profile</profile>
            <acl-profile>#acl-profile</acl-profile>
            <num-subscriptions>5</num-subscriptions>
            <no-local>false</no-local>
            <eliding-enabled>false</eliding-enabled>
            <eliding-topics>0</eliding-topics>
            <eliding-topics-hwm>0</eliding-topics-hwm>
            <dto-local-priority>1</dto-local-priority>
            <dto-network-priority>1</dto-network-priority>
            <client-id>9009</client-id>
            <message-vpn>ci1_bonus</message-vpn>
            <uptime>169d 0h 18m 2s</uptime>
            <slow-subscriber>false</slow-subscriber>
            <client-username>#client-username</client-username>
            <user>\'root\'  Computer: \'solace1\'  Process ID: 2108</user>
            <description>Internal Message Bus</description>
            <software-version>6.0.0.14</software-version>
            <software-date>Oct 23 2012 18:04:53</software-date>
            <platform>Linux26-i386_opt - C SDK</platform>
            <large-message-event-raised>false</large-message-event-raised>
            <message-too-big-event-raised>false</message-too-big-event-raised>
            <parse-error-event-raised>false</parse-error-event-raised>
            <max-eliding-topics-raised>false</max-eliding-topics-raised>
            <total-ingress-flows>0</total-ingress-flows>
            <total-egress-flows>0</total-egress-flows>
            <web-transport-session>N/A</web-transport-session>
          </client>
        </internal-virtual-router>
      </client>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""
        rpc_string_inuse_h2 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client>
        <internal-virtual-router>
          <client>
            <client-address>127.55.55.55:15</client-address>
            <name>#client</name>
            <type>Internal</type>
            <profile>#client-profile</profile>
            <acl-profile>#acl-profile</acl-profile>
            <num-subscriptions>5</num-subscriptions>
            <no-local>false</no-local>
            <eliding-enabled>false</eliding-enabled>
            <eliding-topics>0</eliding-topics>
            <eliding-topics-hwm>0</eliding-topics-hwm>
            <dto-local-priority>1</dto-local-priority>
            <dto-network-priority>1</dto-network-priority>
            <client-id>72</client-id>
            <message-vpn>ci1_bonus</message-vpn>
            <uptime>169d 0h 18m 3s</uptime>
            <slow-subscriber>false</slow-subscriber>
            <client-username>#client-username</client-username>
            <user>\'root\'  Computer: \'solace2\'  Process ID: 9249</user>
            <description>Internal Message Bus</description>
            <software-version>6.0.0.14</software-version>
            <software-date>Oct 23 2012 18:04:53</software-date>
            <platform>Linux26-i386_opt - C SDK</platform>
            <large-message-event-raised>false</large-message-event-raised>
            <message-too-big-event-raised>false</message-too-big-event-raised>
            <parse-error-event-raised>false</parse-error-event-raised>
            <max-eliding-topics-raised>false</max-eliding-topics-raised>
            <total-ingress-flows>0</total-ingress-flows>
            <total-egress-flows>0</total-egress-flows>
            <web-transport-session>N/A</web-transport-session>
          </client>
        </internal-virtual-router>
      </client>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>
"""
        ###
        ### MOCKDATA (not in use)
        ###
        rpc_string_notinuse_h1 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client>
        <internal-virtual-router>
          <client>
            <client-address>127.55.55.55:19</client-address>
            <name>#client</name>
            <type>Internal</type>
            <profile>#client-profile</profile>
            <acl-profile>#acl-profile</acl-profile>
            <num-subscriptions>5</num-subscriptions>
            <no-local>false</no-local>
            <eliding-enabled>false</eliding-enabled>
            <eliding-topics>0</eliding-topics>
            <eliding-topics-hwm>0</eliding-topics-hwm>
            <dto-local-priority>1</dto-local-priority>
            <dto-network-priority>1</dto-network-priority>
            <client-id>2977</client-id>
            <message-vpn>ci1_bonus</message-vpn>
            <uptime>142d 4h 9m 3s</uptime>
            <slow-subscriber>false</slow-subscriber>
            <client-username>#client-username</client-username>
            <user>\'root\'  Computer: \'solace1\'  Process ID: 2108</user>
            <description>Internal Message Bus</description>
            <software-version>6.0.0.14</software-version>
            <software-date>Oct 23 2012 18:04:53</software-date>
            <platform>Linux26-i386_opt - C SDK</platform>
            <large-message-event-raised>false</large-message-event-raised>
            <message-too-big-event-raised>false</message-too-big-event-raised>
            <parse-error-event-raised>false</parse-error-event-raised>
            <max-eliding-topics-raised>false</max-eliding-topics-raised>
            <total-ingress-flows>0</total-ingress-flows>
            <total-egress-flows>0</total-egress-flows>
            <web-transport-session>N/A</web-transport-session>
          </client>
        </internal-virtual-router>
      </client>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""
        rpc_string_notinuse_h2 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client>
        <internal-virtual-router>
          <client>
            <client-address>127.55.55.55:17</client-address>
            <name>#client</name>
            <type>Internal</type>
            <profile>#client-profile</profile>
            <acl-profile>#acl-profile</acl-profile>
            <num-subscriptions>5</num-subscriptions>
            <no-local>false</no-local>
            <eliding-enabled>false</eliding-enabled>
            <eliding-topics>0</eliding-topics>
            <eliding-topics-hwm>0</eliding-topics-hwm>
            <dto-local-priority>1</dto-local-priority>
            <dto-network-priority>1</dto-network-priority>
            <client-id>74</client-id>
            <message-vpn>ci1_bonus</message-vpn>
            <uptime>142d 4h 9m 4s</uptime>
            <slow-subscriber>false</slow-subscriber>
            <client-username>#client-username</client-username>
            <user>\'root\'  Computer: \'solace2\'  Process ID: 9249</user>
            <description>Internal Message Bus</description>
            <software-version>6.0.0.14</software-version>
            <software-date>Oct 23 2012 18:04:53</software-date>
            <platform>Linux26-i386_opt - C SDK</platform>
            <large-message-event-raised>false</large-message-event-raised>
            <message-too-big-event-raised>false</message-too-big-event-raised>
            <parse-error-event-raised>false</parse-error-event-raised>
            <max-eliding-topics-raised>false</max-eliding-topics-raised>
            <total-ingress-flows>0</total-ingress-flows>
            <total-egress-flows>0</total-egress-flows>
            <web-transport-session>N/A</web-transport-session>
          </client>
        </internal-virtual-router>
      </client>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""

        # credentials to test
        username = "ci1_bonus"
        vpnname = "ci1_bonus"

        # store orig method
        orig_get_client = self.solace.get_client

        # test client in use (inuse_h1 / inuse_h2)
        self.solace.get_client = lambda x, y, **z: [xml2dict.parse(rpc_string_inuse_h1),
                                                    xml2dict.parse(rpc_string_inuse_h2)]
        self.assertEqual(True, self.solace.is_client_username_inuse(username, vpnname))

        # test client not in use (notinuse_h1 / notinuse_h2)
        self.solace.get_client = lambda x, y, **z: [xml2dict.parse(rpc_string_notinuse_h1),
                                                    xml2dict.parse(rpc_string_notinuse_h2)]
        self.assertEqual(False, self.solace.is_client_username_inuse(username, vpnname))

        # restore orig method
        self.solace.get_client = orig_get_client

    def test_does_client_username_exist(self):
        from libsolace import xml2dict

        ###
        ### MOCK DATA (found)
        ###
        rpc_string_found_h1 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client-username>
        <client-usernames>
          <client-username>
            <client-username>dev_provtest</client-username>
            <message-vpn>dev_provtest</message-vpn>
            <enabled>true</enabled>
            <guaranteed-endpoint-permission-override>false</guaranteed-endpoint-permission-override>
            <profile>glassfish</profile>
            <acl-profile>dev_provtest</acl-profile>
            <password-configured>true</password-configured>
            <subscription-manager>false</subscription-manager>
            <num-clients>0</num-clients>
            <max-connections>9000</max-connections>
            <num-endpoints>0</num-endpoints>
            <max-endpoints>16000</max-endpoints>
          </client-username>
        </client-usernames>
      </client-username>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""
        rpc_string_found_h2 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client-username>
        <client-usernames>
          <client-username>
            <client-username>dev_provtest</client-username>
            <message-vpn>dev_provtest</message-vpn>
            <enabled>true</enabled>
            <guaranteed-endpoint-permission-override>false</guaranteed-endpoint-permission-override>
            <profile>glassfish</profile>
            <acl-profile>dev_provtest</acl-profile>
            <password-configured>true</password-configured>
            <subscription-manager>false</subscription-manager>
            <num-clients>0</num-clients>
            <max-connections>9000</max-connections>
            <num-endpoints>0</num-endpoints>
            <max-endpoints>16000</max-endpoints>
          </client-username>
        </client-usernames>
      </client-username>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""

        ###
        ### MOCK DATA (notfound)
        ###
        rpc_string_notfound_h1 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client-username>
        <client-usernames>
        </client-usernames>
      </client-username>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""
        rpc_string_notfound_h2 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client-username>
        <client-usernames>
        </client-usernames>
      </client-username>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""

        # credentials to test
        username = 'dev_provtest'
        vpn_name = 'dev_provtest'

        # store orig method
        orig_method = self.solace.get_client_username

        # test nonexistent user (notfound_h1 / notfound_h2)
        self.solace.get_client_username = lambda x, y: [xml2dict.parse(rpc_string_notfound_h1),
                                                        xml2dict.parse(rpc_string_notfound_h2)]
        self.assertEqual(False, self.solace.does_client_username_exist(username, vpn_name))

        # test existing user (found_h1 / found_h2)
        self.solace.get_client_username = lambda x, y: [xml2dict.parse(rpc_string_found_h1),
                                                        xml2dict.parse(rpc_string_found_h2)]
        self.assertEqual(True, self.solace.does_client_username_exist(username, vpn_name))

        # test inconsistent user (notfound_h1 / found_h2)
        self.solace.get_client_username = lambda x, y: [xml2dict.parse(rpc_string_notfound_h1),
                                                        xml2dict.parse(rpc_string_found_h2)]
        with self.assertRaisesRegexp(Exception, "Client username not consistent across all nodes"):
            self.solace.does_client_username_exist(username, vpn_name)

        # restore method
        self.solace.get_client_username = orig_method

    def test_is_client_username_enabled(self):
        from libsolace import xml2dict

        ###
        ### MOCKDATA (enabled)
        ###
        rpc_string_enabled_h1 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client-username>
        <client-usernames>
          <client-username>
            <client-username>dev_provtest</client-username>
            <message-vpn>dev_provtest</message-vpn>
            <enabled>true</enabled>
            <guaranteed-endpoint-permission-override>false</guaranteed-endpoint-permission-override>
            <profile>glassfish</profile>
            <acl-profile>dev_provtest</acl-profile>
            <password-configured>true</password-configured>
            <subscription-manager>false</subscription-manager>
            <num-clients>0</num-clients>
            <max-connections>9000</max-connections>
            <num-endpoints>0</num-endpoints>
            <max-endpoints>16000</max-endpoints>
          </client-username>
        </client-usernames>
      </client-username>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""
        rpc_string_enabled_h2 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client-username>
        <client-usernames>
          <client-username>
            <client-username>dev_provtest</client-username>
            <message-vpn>dev_provtest</message-vpn>
            <enabled>true</enabled>
            <guaranteed-endpoint-permission-override>false</guaranteed-endpoint-permission-override>
            <profile>glassfish</profile>
            <acl-profile>dev_provtest</acl-profile>
            <password-configured>true</password-configured>
            <subscription-manager>false</subscription-manager>
            <num-clients>0</num-clients>
            <max-connections>9000</max-connections>
            <num-endpoints>0</num-endpoints>
            <max-endpoints>16000</max-endpoints>
          </client-username>
        </client-usernames>
      </client-username>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""

        ###
        ### MOCKDATA (disabled)
        ###
        rpc_string_disabled_h1 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client-username>
        <client-usernames>
          <client-username>
            <client-username>dev_provtest</client-username>
            <message-vpn>dev_provtest</message-vpn>
            <enabled>false</enabled>
            <guaranteed-endpoint-permission-override>false</guaranteed-endpoint-permission-override>
            <profile>glassfish</profile>
            <acl-profile>dev_provtest</acl-profile>
            <password-configured>true</password-configured>
            <subscription-manager>false</subscription-manager>
            <num-clients>0</num-clients>
            <max-connections>9000</max-connections>
            <num-endpoints>0</num-endpoints>
            <max-endpoints>16000</max-endpoints>
          </client-username>
        </client-usernames>
      </client-username>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""
        rpc_string_disabled_h2 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client-username>
        <client-usernames>
          <client-username>
            <client-username>dev_provtest</client-username>
            <message-vpn>dev_provtest</message-vpn>
            <enabled>false</enabled>
            <guaranteed-endpoint-permission-override>false</guaranteed-endpoint-permission-override>
            <profile>glassfish</profile>
            <acl-profile>dev_provtest</acl-profile>
            <password-configured>true</password-configured>
            <subscription-manager>false</subscription-manager>
            <num-clients>0</num-clients>
            <max-connections>9000</max-connections>
            <num-endpoints>0</num-endpoints>
            <max-endpoints>16000</max-endpoints>
          </client-username>
        </client-usernames>
      </client-username>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""

        ###
        ### MOCKDATA (notfound)
        ###
        rpc_string_notfound_h1 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client-username>
        <client-usernames>
        </client-usernames>
      </client-username>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""
        rpc_string_notfound_h2 = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <client-username>
        <client-usernames>
        </client-usernames>
      </client-username>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""

        # credentials to test
        username = 'dev_provtest'
        vpn_name = 'dev_provtest'

        # store orig method
        orig_method = self.solace.get_client_username

        # test enabled user
        self.solace.get_client_username = lambda x, y: [xml2dict.parse(rpc_string_enabled_h1),
                                                        xml2dict.parse(rpc_string_enabled_h2)]
        self.assertEqual(True, self.solace.is_client_username_enabled(username, vpn_name))

        # test disabled user
        self.solace.get_client_username = lambda x, y: [xml2dict.parse(rpc_string_disabled_h1),
                                                        xml2dict.parse(rpc_string_disabled_h2)]
        self.assertEqual(False, self.solace.is_client_username_enabled(username, vpn_name))

        # test inconsistent user
        self.solace.get_client_username = lambda x, y: [xml2dict.parse(rpc_string_enabled_h1),
                                                        xml2dict.parse(rpc_string_disabled_h2)]
        with self.assertRaisesRegexp(Exception, "Enabled and disabled on some nodes"):
            self.solace.is_client_username_enabled(username, vpn_name)

        # test nonexistent user
        self.solace.get_client_username = lambda x, y: [xml2dict.parse(rpc_string_notfound_h1),
                                                        xml2dict.parse(rpc_string_notfound_h2)]
        with self.assertRaisesRegexp(Exception, "Client username dev_provtest not found"):
            self.solace.is_client_username_enabled(username, vpn_name)

        # restore method
        self.solace.get_client_username = orig_method

    def test_get_client_username_queues(self):
        from libsolace import xml2dict

        ###
        ### MOCKDATA (found)
        ###
        rpc_string_found = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <queue>
        <queues>
          <queue>
            <name>testqueue1</name>
            <info>
              <message-vpn>test_dev_keghol</message-vpn>
              <durable>true</durable>
              <endpt-id>2726</endpt-id>
              <type>Primary</type>
              <ingress-config-status>Up</ingress-config-status>
              <egress-config-status>Up</egress-config-status>
              <access-type>non-exclusive</access-type>
              <owner>test_dev_keghol</owner>
              <created-by-mgmt>Yes</created-by-mgmt>
              <others-permission>Consume (1100)</others-permission>
              <quota>100</quota>
              <respect-ttl>No</respect-ttl>
              <reject-msg-to-sender-on-discard>Yes</reject-msg-to-sender-on-discard>
              <bind-time-forwarding-mode>Store-And-Forward</bind-time-forwarding-mode>
              <num-messages-spooled>0</num-messages-spooled>
              <current-spool-usage-in-mb>0</current-spool-usage-in-mb>
              <high-water-mark-in-mb>9.99985</high-water-mark-in-mb>
              <total-delivered-unacked-msgs>0</total-delivered-unacked-msgs>
              <max-delivered-unacked-msgs-per-flow>250000</max-delivered-unacked-msgs-per-flow>
              <total-acked-msgs-in-progress>0</total-acked-msgs-in-progress>
              <max-redelivery>0</max-redelivery>
              <reject-low-priority-msg-limit>0</reject-low-priority-msg-limit>
              <low-priority-msg-congestion-state>Disabled</low-priority-msg-congestion-state>
              <max-message-size>10000000</max-message-size>
              <bind-count>0</bind-count>
              <bind-count-threshold-high-percentage>80</bind-count-threshold-high-percentage>
              <bind-count-threshold-high-clear-percentage>60</bind-count-threshold-high-clear-percentage>
              <max-bind-count>1000</max-bind-count>
              <topic-subscription-count>0</topic-subscription-count>
              <network-topic>#P2P/QUE/v:solace1/testqueue1</network-topic>
              <egress-selector-present>No</egress-selector-present>
              <event>
                <event-thresholds>
                  <name>bind-count</name>
                  <set-value>800</set-value>
                  <clear-value>600</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
                <event-thresholds>
                  <name>spool-usage</name>
                  <set-value>80</set-value>
                  <clear-value>60</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
                <event-thresholds>
                  <name>reject-low-priority-msg-limit</name>
                  <set-value>0</set-value>
                  <clear-value>0</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
                <event-thresholds>
                  <name>reject-low-priority-msg-limit</name>
                  <set-value>0</set-value>
                  <clear-value>0</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
              </event>
            </info>
          </queue>
        </queues>
      </queue>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""
        rpc_string_multiple_found = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <queue>
        <queues>
          <queue>
            <name>testqueue1</name>
            <info>
              <message-vpn>test_dev_keghol</message-vpn>
              <durable>true</durable>
              <endpt-id>2726</endpt-id>
              <type>Primary</type>
              <ingress-config-status>Up</ingress-config-status>
              <egress-config-status>Up</egress-config-status>
              <access-type>non-exclusive</access-type>
              <owner>test_dev_keghol</owner>
              <created-by-mgmt>Yes</created-by-mgmt>
              <others-permission>Consume (1100)</others-permission>
              <quota>100</quota>
              <respect-ttl>No</respect-ttl>
              <reject-msg-to-sender-on-discard>Yes</reject-msg-to-sender-on-discard>
              <bind-time-forwarding-mode>Store-And-Forward</bind-time-forwarding-mode>
              <num-messages-spooled>0</num-messages-spooled>
              <current-spool-usage-in-mb>0</current-spool-usage-in-mb>
              <high-water-mark-in-mb>9.99985</high-water-mark-in-mb>
              <total-delivered-unacked-msgs>0</total-delivered-unacked-msgs>
              <max-delivered-unacked-msgs-per-flow>250000</max-delivered-unacked-msgs-per-flow>
              <total-acked-msgs-in-progress>0</total-acked-msgs-in-progress>
              <max-redelivery>0</max-redelivery>
              <reject-low-priority-msg-limit>0</reject-low-priority-msg-limit>
              <low-priority-msg-congestion-state>Disabled</low-priority-msg-congestion-state>
              <max-message-size>10000000</max-message-size>
              <bind-count>0</bind-count>
              <bind-count-threshold-high-percentage>80</bind-count-threshold-high-percentage>
              <bind-count-threshold-high-clear-percentage>60</bind-count-threshold-high-clear-percentage>
              <max-bind-count>1000</max-bind-count>
              <topic-subscription-count>0</topic-subscription-count>
              <network-topic>#P2P/QUE/v:solace1/testqueue1</network-topic>
              <egress-selector-present>No</egress-selector-present>
              <event>
                <event-thresholds>
                  <name>bind-count</name>
                  <set-value>800</set-value>
                  <clear-value>600</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
                <event-thresholds>
                  <name>spool-usage</name>
                  <set-value>80</set-value>
                  <clear-value>60</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
                <event-thresholds>
                  <name>reject-low-priority-msg-limit</name>
                  <set-value>0</set-value>
                  <clear-value>0</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
                <event-thresholds>
                  <name>reject-low-priority-msg-limit</name>
                  <set-value>0</set-value>
                  <clear-value>0</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
              </event>
            </info>
          </queue>
          <queue>
            <name>testqueue2</name>
            <info>
              <message-vpn>test_dev_keghol</message-vpn>
              <durable>true</durable>
              <endpt-id>2726</endpt-id>
              <type>Primary</type>
              <ingress-config-status>Up</ingress-config-status>
              <egress-config-status>Up</egress-config-status>
              <access-type>non-exclusive</access-type>
              <owner>other_owner</owner>
              <created-by-mgmt>Yes</created-by-mgmt>
              <others-permission>Consume (1100)</others-permission>
              <quota>100</quota>
              <respect-ttl>No</respect-ttl>
              <reject-msg-to-sender-on-discard>Yes</reject-msg-to-sender-on-discard>
              <bind-time-forwarding-mode>Store-And-Forward</bind-time-forwarding-mode>
              <num-messages-spooled>0</num-messages-spooled>
              <current-spool-usage-in-mb>0</current-spool-usage-in-mb>
              <high-water-mark-in-mb>9.99985</high-water-mark-in-mb>
              <total-delivered-unacked-msgs>0</total-delivered-unacked-msgs>
              <max-delivered-unacked-msgs-per-flow>250000</max-delivered-unacked-msgs-per-flow>
              <total-acked-msgs-in-progress>0</total-acked-msgs-in-progress>
              <max-redelivery>0</max-redelivery>
              <reject-low-priority-msg-limit>0</reject-low-priority-msg-limit>
              <low-priority-msg-congestion-state>Disabled</low-priority-msg-congestion-state>
              <max-message-size>10000000</max-message-size>
              <bind-count>0</bind-count>
              <bind-count-threshold-high-percentage>80</bind-count-threshold-high-percentage>
              <bind-count-threshold-high-clear-percentage>60</bind-count-threshold-high-clear-percentage>
              <max-bind-count>1000</max-bind-count>
              <topic-subscription-count>0</topic-subscription-count>
              <network-topic>#P2P/QUE/v:solace1/testqueue1</network-topic>
              <egress-selector-present>No</egress-selector-present>
              <event>
                <event-thresholds>
                  <name>bind-count</name>
                  <set-value>800</set-value>
                  <clear-value>600</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
                <event-thresholds>
                  <name>spool-usage</name>
                  <set-value>80</set-value>
                  <clear-value>60</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
                <event-thresholds>
                  <name>reject-low-priority-msg-limit</name>
                  <set-value>0</set-value>
                  <clear-value>0</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
                <event-thresholds>
                  <name>reject-low-priority-msg-limit</name>
                  <set-value>0</set-value>
                  <clear-value>0</clear-value>
                  <set-percentage>80</set-percentage>
                  <clear-percentage>60</clear-percentage>
                </event-thresholds>
              </event>
            </info>
          </queue>
        </queues>
      </queue>
    </show>
  </rpc>
<execute-result code="ok"/>
</rpc-reply>"""
        rpc_string_not_active = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <queue>
<!-- ERROR: message-spool operational status is not AD-ACTIVE
 -->
      </queue>
    </show>
  </rpc>
<execute-result code="fail" reason="fail" reasonCode="2"/>
</rpc-reply>"""
        rpc_string_not_found = """<rpc-reply semp-version="soltr/6_0">
  <rpc>
    <show>
      <queue>
        <queues>
<!-- ERROR: Message VPN \'sdjfio\' not found.
 -->
        </queues>
      </queue>
    </show>
  </rpc>
<execute-result code="fail" reason="not found" reasonCode="6"/>
</rpc-reply>"""

        # credentials
        username = 'test_dev_keghol'
        vpn_name = 'test_dev_keghol'

        # store orig method
        orig_method = self.solace.get_queue

        # test user / vpn owning queues
        self.solace.get_queue = lambda x, y, **z: [xml2dict.parse(rpc_string_found),
                                                   xml2dict.parse(rpc_string_not_active)]
        self.assertEqual(['testqueue1'], self.solace.get_client_username_queues(username, vpn_name))

        # test user / vpn owning queues
        self.solace.get_queue = lambda x, y, **z: [xml2dict.parse(rpc_string_multiple_found),
                                                   xml2dict.parse(rpc_string_not_active)]
        self.assertEqual(['testqueue1'], self.solace.get_client_username_queues(username, vpn_name))

        # test user / vpn with no queues found in VPN
        self.solace.get_queue = lambda x, y, **z: [xml2dict.parse(rpc_string_not_found),
                                                   xml2dict.parse(rpc_string_not_active)]
        self.assertEqual([], self.solace.get_client_username_queues(username, vpn_name))

        # test user / vpn with no ownership of queues
        username = 'i_dont_have_any_queues'
        self.solace.get_queue = lambda x, y, **z: [xml2dict.parse(rpc_string_found),
                                                   xml2dict.parse(rpc_string_not_active)]
        self.assertEqual([], self.solace.get_client_username_queues(username, vpn_name))

        # restore method
        self.solace.get_queue = orig_method
