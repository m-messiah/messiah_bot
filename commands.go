package main

import (
	log "github.com/sirupsen/logrus"
	"net/http"
	"os/exec"
	"strings"
)

func allowAccess(w http.ResponseWriter, chatID int64, command string) bool {
	for _, admin := range config.Admins {
		if chatID == admin {
			return true
		}
	}
	answerMessage(w, chatID, command, "Доступ ограничен")
	return false
}

func isCommand(text, command string) bool {
	if strings.Index(text, command) == 0 {
		if strings.Contains(strings.ToLower(text), "@"+strings.ToLower(config.Name)) || !strings.Contains(text, "@") {
			return true
		}
	}
	return false
}

func handleCommand(w http.ResponseWriter, updateMessage *Message, botLog *log.Entry) {
	messageText := *updateMessage.Text

	if isCommand(messageText, "/start") {
		command := "/start"
		botLog.WithFields(log.Fields{"command": command}).Debug("Start")
		answerMessage(w, updateMessage.Chat.ID, command, "Привет! А тебе точно сюда надо?")
		return
	}

	if isCommand(messageText, "/stop") {
		command := "/stop"
		botLog.WithFields(log.Fields{"command": command}).Debug("Start")
		answerMessage(w, updateMessage.Chat.ID, command, "Это ничего не изменит...")
		return
	}

	if isCommand(messageText, "/help") {
		command := "/help"
		botLog.WithFields(log.Fields{"command": command}).Debug("Start")
		answerMessage(w, updateMessage.Chat.ID, command, "Еще не готово")
		return
	}

	// Below are admin restricted commands
	if !allowAccess(w, updateMessage.Chat.ID, messageText) {
		return
	}

	if isCommand(messageText, "/uptime") {
		command := "/uptime"
		output, ok := execSysCommand(botLog, "uptime")
		if ok {
			answerMessage(w, updateMessage.Chat.ID, command, output)
		} else {
			answerSticker(w, updateMessage.Chat.ID, command, "Ждун Error")
		}
		return
	}

	if isCommand(messageText, "/restart_tor") {
		command := "/restart_tor"
		output, ok := execSysCommand(botLog, "sudo", "systemctl", "restart", "tor")
		if ok {
			answerSticker(w, updateMessage.Chat.ID, command, "Я Сделяль")
		} else {
			answerMessage(w, updateMessage.Chat.ID, command, output)
		}
		return
	}

	if isCommand(messageText, "/restart_nginx") {
		command := "/restart_nginx"
		output, ok := execSysCommand(botLog, "sudo", "systemctl", "restart", "nginx")
		if ok {
			answerSticker(w, updateMessage.Chat.ID, command, "Я Сделяль")
		} else {
			answerMessage(w, updateMessage.Chat.ID, command, output)
		}
		return
	}

	if isCommand(messageText, "/restart_me") {
		command := "/restart_me"
		go execSysCommand(botLog, "sudo", "systemctl", "restart", "bot")
		answerSticker(w, updateMessage.Chat.ID, command, "Я Сделяль")
		return
	}

	answerSticker(w, updateMessage.Chat.ID, messageText, "meh")
}

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
