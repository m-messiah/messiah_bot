package main

import (
	log "github.com/sirupsen/logrus"
	"net/http"
	"strings"
)

func handleText(w http.ResponseWriter, updateMessage *Message, botLog *log.Entry) {
	messageText := *updateMessage.Text
	chatID := updateMessage.Chat.ID
	restart := []string{"restart", "reboot", "перезагруз", "рестарт"}
	status := []string{"status", "статус", "состояние", "check"}

	if strContainsAny(messageText, restart...) {
		switch {
		case strings.Contains(messageText, "tor"):
			executeRestart(w, chatID, botLog, "tor")
		case strings.Contains(messageText, "nginx"):
			executeRestart(w, chatID, botLog, "nginx")
		case strings.Contains(messageText, "me"), strings.Contains(messageText, "bot"):
			executeRestartMe(w, chatID, botLog)
		default:
			answerSticker(w, chatID, "restart", "НетПути")
		}
		return
	}

	if strContainsAny(messageText, status...) {
		switch {
		case strings.Contains(messageText, "tor"):
			executeStatus(w, chatID, botLog, "tor")
		case strings.Contains(messageText, "nginx"):
			executeStatus(w, chatID, botLog, "nginx")
		case strings.Contains(messageText, "me"), strings.Contains(messageText, "bot"):
			executeStatus(w, chatID, botLog, "bot")
		default:
			answerSticker(w, chatID, "status", "НетПути")
		}
		return
	}

	if strContainsAny(messageText, "включи комп", "poweron") {
		executePoweron(w, chatID, botLog)
		return
	}

	answerMessage(w, chatID, "None", "Я пока умею только команды")
}

func strContainsAny(s string, substrings ...string) bool {
	for _, substr := range substrings {
		if strings.Contains(s, substr) {
			return true
		}
	}
	return false
}
