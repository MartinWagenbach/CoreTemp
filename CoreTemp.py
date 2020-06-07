#!/usr/bin/python3
from configparser import ConfigParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from smtplib import SMTP
import subprocess as sp
import time
from os.path import expanduser
from config_path import ConfigPath


last_mail = None


def readConfig():
    cp = ConfigParser()

    cp["default"] = {
        "log_path": "stdout",
        "update_interval": 60,
        "mail_interval": 900,
        "warning_threshold": 70,
        "panic_threshold": 90,
    }

    system_cfg_path = Path("/etc/CoreTemp.ini")
    local_cfg_path = ConfigPath("", "CoreTemp", "ini")

    if system_cfg_path.is_file():
        cp.read(system_cfg_path)
    if not local_cfg_path.readFilePath() is None:
        cp.read(local_cfg_path.readFilePath())

    return cp


def sendMail(cfg, body, subject):
    if not cfg.has_option("config", "smtp_server") or \
            not cfg.has_option("config", "e_mail") or \
            not cfg.has_option("config", "password") or \
            not cfg.has_option("config", "receiver"):
        print("E-Mails have not been configured.")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = cfg["config"]["e_mail"]
    message["To"] = cfg["config"]["receiver"]

    message.attach(MIMEText(body, "plain"))
    server = SMTP(cfg["config"]["smtp_server"])
    server.starttls()
    server.login(cfg["config"]["e_mail"], cfg["config"]["password"])
    server.sendmail(cfg["config"]["e_mail"], cfg["config"]["receiver"], message.as_string())
    server.quit()


def measureTemp(cfg):
    global last_mail
    temp = float(sp.check_output(["vcgencmd", "measure_temp"]).decode(encoding="utf-8").replace("temp=", "")
                 .replace("'C", ""))
    psAux = sp.check_output(["ps", "aux"]).decode(encoding="utf-8")

    if temp >= float(cfg["config"]["warning_threshold"]) and \
            (last_mail is None or (time.time() - last_mail) >= float(cfg["config"]["mail_interval"])):
        sendMail(cfg, psAux, "Raspberry Pi temperatur at {:3.2f} °C".format(temp))
        last_mail = time.time()

    if temp >= float(cfg["config"]["panic_threshold"]):
        sendMail(cfg, "", "Raspberry Pi overheating! Shutting down.")
        sp.run("poweroff")

    if config["config"]["log_path"] == "stdout":
        print("{} >> {: 3.2f} °C\n".format(time.strftime("%d.%m.%Y %H:%M:%S"), temp))
    else:
        file = open(expanduser(cfg["config"]["log_path"]), "a")
        file.write("{} >> {: 3.2f} °C\n".format(time.strftime("%d.%m.%Y %H:%M:%S"), temp))
        file.close()


config = readConfig()

while True:
    measureTemp(config)
    time.sleep(int(config["config"]["update_interval"]))
