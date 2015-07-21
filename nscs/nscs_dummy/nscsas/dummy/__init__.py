from pecan.rest import RestController
import wsmeext.pecan as wsme_pecan

from nscs.ocas_utils.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class DUMMYController(RestController):

    @wsme_pecan.wsexpose(None, status_code=204)
    def post(self):
        LOG.debug(_("Dummy Create Request received"))

    @wsme_pecan.wsexpose(None, status_code=204)
    def put(self):
        LOG.debug(_("Dummy Update Request received"))

    @wsme_pecan.wsexpose(None)
    def get_all(self):
        LOG.debug(_("Dummy List Request received"))
        return [{'dummys': {}}]

    @wsme_pecan.wsexpose(None)
    def get_one(self):
        LOG.debug(_("Dummy Get Request received"))
        return {'dummy': {}}

    @wsme_pecan.wsexpose(None, status_code=204)
    def delete(self):
        LOG.debug(_("Dummy Delete Request received"))