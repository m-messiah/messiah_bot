package main

import (
	log "github.com/sirupsen/logrus"
	"net/http"
	"os/exec"
	"strings"
)

func execSysCommand(botLog *log.Entry, command string, args ...string) (string, bool) {
	ok := true
	botLog.WithFields(log.Fields{"command": command}).Debug("Start")
	out, err := exec.Command(command, args...).CombinedOutput()
	if err != nil {
		botLog.WithFields(log.Fields{"command": command, "error": err.Error()}).Error(string(out))
		out = append(out, []byte(err.Error())...)
		ok = false
	}
	return string(out), ok
}

func executeUptime(w http.ResponseWriter, chatID int64, botLog *log.Entry) {
	command := "uptime"
	output, ok := execSysCommand(botLog, "uptime")
	if ok {
		answerMessage(w, chatID, command, output)
	} else {
		answerSticker(w, chatID, command, "Ждун Error")
	}
}

func executeRestart(w http.ResponseWriter, chatID int64, botLog *log.Entry, service string) {
	command := "restart " + service
	output, ok := execSysCommand(botLog, "sudo", "systemctl", "restart", service)
	if ok {
		answerSticker(w, chatID, command, "Я Сделяль")
	} else {
		answerMessage(w, chatID, command, output)
	}
}

func executeRestartMe(w http.ResponseWriter, chatID int64, botLog *log.Entry) {
	go execSysCommand(botLog, "sudo", "systemctl", "restart", "bot")
	answerSticker(w, chatID, "restart bot", "Я Сделяль")
}

func executeStatus(w http.ResponseWriter, chatID int64, botLog *log.Entry, service string) {
	command := "status " + service
	output, _ := execSysCommand(botLog, "sudo", "systemctl", "status", service)
	output_splitted := strings.Split(output, "\n")
	output_head := output_splitted[0] + "\n" + output_splitted[2]
	answerMessage(w, chatID, command, output_head)
}

func executePoweron(w http.ResponseWriter, chatID int64, botLog *log.Entry) {
	command := "power on"
	err := SendMagicPacket(config.MacAddr)
	if err == nil {
		answerSticker(w, chatID, command, "Я Сделяль")
	} else {
		botLog.Error(err)
		answerSticker(w, chatID, command, "Ждун Error")
	}
}
