"""
FortiGate configuration check utility
"""
import logging
from pathlib import Path
from typing import Any, List

import typer

from fotoobo.exceptions import FotooboError, FotooboWarning
from fotoobo.fortinet.fortigate_config import FortiGateConfig
from fotoobo.fortinet.fortigate_config_check import FortiGateConfigCheck
from fotoobo.fortinet.fortigate_info import FortiGateInfo
from fotoobo.helpers.files import load_yaml_file
from fotoobo.helpers.result import Result

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


def check(config: Path, bundles: Path) -> Result[List[str]]:
    """
    The FortiGate configuration check

    Args:
        config:  The configuration to check (either a file or directory)
                 in case it's a directory all .conf files in it will be checked.
        bundles: The check bundle to check the configuration against

    Raises:
        FotooboWarning: If there is no configuration file to check
        FotooboError:   If the configuration file cannot be read
    """
    files: List[Path] = []
    config = Path(config)

    if config.is_file():
        files.append(config)

    elif config.is_dir():
        log.debug("Given config is a directory")
        files = [file for file in config.iterdir() if file.suffix == ".conf"]

    else:
        log.error("No valid configuration file")

    if not files:
        log.warning("There are no configuration files to check")
        raise FotooboWarning("There are no configuration files to check")

    bundles = Path(bundles)
    if bundles.is_file():
        checks = load_yaml_file(bundles)

    else:
        log.error("No valid bundle file")
        raise FotooboError("No valid bundle file")

    total_results: int = 0
    result = Result[List[str]]()

    for file in files:
        try:
            fortigate_config = FortiGateConfig.parse_configuration_file(file)
            conf_check = FortiGateConfigCheck(fortigate_config, checks, result)

        except FotooboWarning as warn:
            log.warning(warn.message)
            continue

        conf_check.execute_checks()

        num_results = len(result.get_messages(fortigate_config.info.hostname))
        log.info("All checks in '%s' done with '%s' messages", file.name, num_results)
        total_results += num_results

    log.info("All checks done with '%s' messages", total_results)

    if total_results == 0:
        result.push_message("fotoobo", "There were no errors in the configuration file(s)")

    return result


def get(config: Path, scope: str = "", path: str = "") -> Result[FortiGateInfo]:
    """
    The FortiGate get configuration utility.

    Args:
        config: The configuration to get the information from (either a file or directory)
                In case it's a directory all .conf files in it will be checked.

    Returns:
        Configuration as result object

    Raises:
        FotooboWarning: FotooboWarning
    """
    files: List[Path] = []
    if config.is_file():
        files.append(config)

    elif config.is_dir():
        log.debug("Given config is a directory")
        files = [file for file in config.iterdir() if file.is_file() and file.suffix == ".conf"]

    if not files:
        log.warning("There are no configuration files")
        raise FotooboWarning("There are no configuration files")

    result = Result[Any]()

    for file in files:
        conf = FortiGateConfig.parse_configuration_file(file)
        output = conf.get_configuration(scope, path)
        result.push_result(conf.info.hostname, output)

    return result


def info(config: Path) -> Result[FortiGateInfo]:
    """
    The FortiGate configuration information utility.

    Args:
        config: The configuration to get the information from (either a file or directory)
                In case it's a directory all .conf files in it will be checked.

    Returns:
        FortiGate information as result object

    Raises:
        FotooboWarning: If no configuration file could be found
    """
    files: List[Path] = []
    if config.is_file():
        files.append(config)

    elif config.is_dir():
        log.debug("Given config is a directory")
        files = [file for file in config.iterdir() if file.is_file() and file.suffix == ".conf"]

    if not files:
        log.warning("There are no configuration files")
        raise FotooboWarning("There are no configuration files")

    result = Result[FortiGateInfo]()

    for file in files:
        conf = FortiGateConfig.parse_configuration_file(file)
        result.push_result(conf.info.hostname, conf.info)

    return result
