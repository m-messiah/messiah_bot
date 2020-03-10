package main

import (
	log "github.com/sirupsen/logrus"
	"net/http"
	"strings"
)

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

	switch {
	case isCommand(messageText, "/uptime"):
		executeUptime(w, chatID, botLog)
	case isCommand(messageText, "/restart_me"), isCommand(messageText, "/restart_bot"):
		executeRestartMe(w, chatID, botLog)
	case isCommand(messageText, "/restart_"):
		command_args := strings.SplitN(messageText, "_", 2)
		executeRestart(w, chatID, botLog, command_args[1])
	case isCommand(messageText, "/status_"):
		command_args := strings.SplitN(messageText, "_", 2)
		executeStatus(w, chatID, botLog, command_args[1])
	case isCommand(messageText, "/poweron_"):
		command_args := strings.SplitN(messageText, "_", 2)
		device, ok := config.Devices[command_args[1]]
		if !ok {
			log.WithFields(log.Fields{"chat": chatID, "command": "power on", "device": command_args[1]}).Error("Device not found")
			answerSticker(w, chatID, "power on", "НетПути")
			return
		}
		executePoweron(w, chatID, botLog, device)
	case isCommand(messageText, "/poweroff_"):
		command_args := strings.SplitN(messageText, "_", 2)
		_, ok := config.Devices[command_args[1]]
		if !ok {
			log.WithFields(log.Fields{"chat": chatID, "command": "power off", "device": command_args[1]}).Error("Device not found")
			answerSticker(w, chatID, "power off", "НетПути")
			return
		}
		executePoweroff(w, chatID, botLog, command_args[1])
	default:
		answerSticker(w, chatID, messageText, "meh")
	}
}
