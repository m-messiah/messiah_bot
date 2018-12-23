package main

import (
	log "github.com/sirupsen/logrus"
	"net/http"
	"strings"
)

func allowAccess(w http.ResponseWriter, chatID int64, command string) bool {
	for _, admin := range config.Admins {
		if chatID == admin {
			return true
		}
	}
	answerSticker(w, chatID, command, "НетПути")
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
	chatID := updateMessage.Chat.ID

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

	switch {
	case isCommand(messageText, "/uptime"):
		executeUptime(w, chatID, botLog)
	case isCommand(messageText, "/restart_tor"):
		executeRestart(w, chatID, botLog, "tor")
	case isCommand(messageText, "/restart_nginx"):
		executeRestart(w, chatID, botLog, "nginx")
	case isCommand(messageText, "/restart_me"), isCommand(messageText, "/restart_bot"):
		executeRestartMe(w, chatID, botLog)
	case isCommand(messageText, "/poweron_comp"):
		executePoweron(w, chatID, botLog, config.Devices["comp"])
	case isCommand(messageText, "/poweron_tv"):
		executePoweron(w, chatID, botLog, config.Devices["tv"])
	default:
		answerSticker(w, chatID, messageText, "meh")
	}
}
