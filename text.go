package main

import (
	log "github.com/sirupsen/logrus"
	"net/http"
	"strings"
	"unicode"
)

func handleText(w http.ResponseWriter, updateMessage *Message, botLog *log.Entry) {
	messageText := *updateMessage.Text
	chatID := updateMessage.Chat.ID
	restart := []string{"restart", "reboot", "перезагрузи", "рестарт", "перезагрузить"}
	status := []string{"status", "статус", "состояние", "check", "проверь"}
	torName := []string{"tor", "тор", "прокси", "proxy"}
	nginxName := []string{"nginx", "веб", "нгинкс", "фронт"}
	botName := []string{"bot", "me", "себя", "бот"}
	compName := []string{"включи", "комп", "poweron", "power", "играть"}

	if strContainsAny(messageText, restart...) {
		switch {
		case strContainsAny(messageText, torName...):
			executeRestart(w, chatID, botLog, "tor")
		case strContainsAny(messageText, nginxName...):
			executeRestart(w, chatID, botLog, "nginx")
		case strContainsAny(messageText, botName...):
			executeRestartMe(w, chatID, botLog)
		default:
			answerSticker(w, chatID, "restart", "НетПути")
		}
		return
	}

	if strContainsAny(messageText, status...) {
		switch {
		case strContainsAny(messageText, torName...):
			executeStatus(w, chatID, botLog, "tor")
		case strContainsAny(messageText, nginxName...):
			executeStatus(w, chatID, botLog, "nginx")
		case strContainsAny(messageText, botName...):
			executeStatus(w, chatID, botLog, "bot")
		default:
			answerSticker(w, chatID, "status", "НетПути")
		}
		return
	}

	if strContainsAny(messageText, compName...) {
		executePoweron(w, chatID, botLog)
		return
	}

	answerMessage(w, chatID, "None", "Я пока умею только команды")
}

func strContainsAny(s string, substrings ...string) bool {
	splitFunc := func(c rune) bool {
		return !unicode.IsLetter(c) && !unicode.IsNumber(c) && (c != '-')
	}
	fields := strings.FieldsFunc(s, splitFunc)
	for _, field := range fields {
		for _, substr := range substrings {
			if strings.EqualFold(field, substr) {
				return true
			}
		}
	}
	return false
}
