# /usr/bin/env python3.6

from source import *
from subprocess import run, PIPE

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import os
import time

cwd = str(os.getcwd())

xpaths = {
    'navAccount': '//*[@id="nav-1"]/div/a[1]',
    'submenuUser': '//*[@id="1-1"]',
    'submenuGroup': '//*[@id="1-0"]',
    'navPlugins': '//*[@id="nav-9"]/div/a[1]',
    'submenuAvailable': '//*[@id="9-0"]',
    'submenuInstalled': '//*[@id="9-1"]',
    'buttonSave': '//*[contains(text(), "Save")]',
    'navStorage': '//*[@id="nav-5"]/div/a[1]',
    'submenuPool': '//*[@id="5-0"]',
    'poolID': '//*[@id="expansionpanel_zfs_',
    'submenuDisks': '//*[@id="5-3"]',
    'poolDetach': '//*[@id="action_button_Detach"]',
    'pooldestroyCheckbox': '//*[@id="destroy"]/mat-checkbox/label/div',
    'poolconfirmdestroyCheckbox': '//*[@id="confirm"]/mat-checkbox/label/div',
    'confirmCheckbox': '//*[@id="confirm-dialog__confirm-checkbox"]/label/div',
    'confirmsecondaryCheckbox': '//*[@id="confirm-dialog__secondary-checkbox"]/label/div',
    'deleteButton': '//*[contains(@name, "ok_button")]',
    'detachButton': '//*[contains(@name, "Detach_button")]',
    'closeButton': '//*[contains(text(), "Close")]',
    'turnoffConfirm': "//span[contains(.,'STOP')]"
}

services_switch_xpath = {
    'afp': "//div[@id='overlay__AFP']",
    'dc': "//div[@id='overlay__Domain Controller']",
    'dns': "//div[@id='overlay__Dynamic DNS']",
    'nfs': "//div[@id='overlay__NFS']",
    'ftp': "//div[@id='overlay__FTP']",
    'iscsi': "//div[@id='overlay__iSCSI']",
    'lldp': "//div[@id='overlay__LLDP']",
    'smb': "//div[@id='overlay__SMB']",
    'ssh': "//div[@id='overlay__SSH']",
    'webdav': "//div[@id='overlay__WebDAV']"
}


def ssh_test(command, username, passwrd, host):
    cmd = [] if passwrd is None else ["sshpass", "-p", passwrd]
    cmd += [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "VerifyHostKeyDNS=no",
        f"{username}@{host}",
    ]
    cmd += command.split()
    process = run(cmd, stdout=PIPE, universal_newlines=True)
    output = process.stdout
    if process.returncode != 0:
        return {'result': False, 'output': output}
    else:
        return {'result': True, 'output': output}


# method to test if an element is present
def is_element_present(driver, xpath):
    try:
        driver.find_element(by=By.XPATH, value=xpath)
    except NoSuchElementException:
        return False
    return True


def wait_on_element(driver, xpath, scriptname, testname):
    num = 0
    while is_element_present(driver, xpath) is False:
        if num == 120:
            take_screenshot(driver, scriptname, testname)
            return False
        else:
            num += 1
        time.sleep(1)
    return True


def error_check(driver):
    title_xpath = "//h1[contains(.,'report_problem error')]"
    dialog_xpath = '//error-dialog/div/span'
    tearDown_xpath = "//span[contains(.,'More info...')]"
    traceback_xpath = "//div[2]/textarea"
    closeButton = '//*[contains(text(), "Close")]'
    if is_element_present(driver, title_xpath):
        dialog = driver.find_element_by_xpath(dialog_xpath)
        dialog_text = dialog.text
        driver.find_element_by_xpath(tearDown_xpath).click()
        traceback = driver.find_element_by_xpath(traceback_xpath)
        traceback_text = traceback.text
        driver.find_element_by_xpath(closeButton).click()

        return {'result': False, 'dialog': dialog_text, 'traceback': traceback_text}
    return {'result': True, 'dialog': '', 'traceback': ''}


# screenshot function
def take_screenshot(driver, scriptname, testname):
    time.sleep(1)
    png_file = cwd + "/screenshot/" + scriptname + "-" + testname + ".png"
    driver.save_screenshot(png_file)


# status check for services
def status_check(driver, which):
    toggle_status = driver.find_element_by_xpath(services_switch_xpath[which])
    status_data = toggle_status.get_attribute("class")
    print(status_data)
    if (status_data == "mat-slide-toggle mat-accent ng-star-inserted mat-checked"):
        print("current status is: RUNNING")
    else:
        print("current status is: STOPPED")
    # get the status data
    print("current status is: " + services_switch_xpath[which])


def status_change(driver, which):
    driver.find_element_by_xpath(services_switch_xpath[which]).click()
    time.sleep(2)
    if is_element_present(driver, xpaths['turnoffConfirm']):
        driver.find_element_by_xpath(xpaths['turnoffConfirm']).click()
        time.sleep(2)
