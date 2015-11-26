class AbstractSolaceCMDB(object):

    # def __init__(self, *args, **kwargs):
    #     raise NotImplementedError( "Should have implemented this" )

    """
    Abstract implementation of the CMDB getter for vpns, users and queues
    """
    def get_vpns_by_owner(self, owner_name, environment='dev', **kwargs):
        """
        [
           {
              'owner':'SolaceTest',
              'spool_size':'4096',
              'password':'d0nt_u5se_thIs',
              'name':'%s_testvpn'
           }
        ]
        """
        raise NotImplementedError( "Should have implemented this" )

    def get_users_of_vpn(self, vpn_name, environment='dev', **kwargs):
        """
        [
           {
              'username':'%s_testproductA',
              'password':'passwordX'
           },
           {
              'username':'%s_testproductB',
              'password':'passwordX'
           }
        ]
        """
        raise NotImplementedError( "Should have implemented this" )

    def get_queues_of_vpn(self, vpn_name, environment='dev', **kwargs):
        """
        [
           {
              "exclusive":"true",
              "type":"",
              "name":"testqueue1",
              "queue_size":"4096"
           },
           {
              "exclusive":"false",
              "type":"",
              "name":"testqueue2",
              "queue_size":"4096"
           }
        ]
        """
        raise NotImplementedError( "Should have implemented this" )
