"""
FortiAnalyzer get version utility
"""
import logging

from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def version(host: str) -> Result[str]:
    """
    FortiAnalyzer get version

    Args:
        host: Host defined in inventory

    Returns:
        The version string per FAZ

    Raises:
        FotooboWarning: FotooboWarning
    """
    result = Result[str]()
    inventory = Inventory(config.inventory_file)
    assets = inventory.get(host, "fortianalyzer")
    log.debug("FortiAnalyzer get version ...")
    assets[host].login()
    faz_version = assets[host].get_version()
    assets[host].logout()
    result.push_result(host, faz_version)
    return result
