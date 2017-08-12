package main

import (
	"encoding/json"
	log "github.com/sirupsen/logrus"
	"io/ioutil"
	"net/http"
	"net/url"
	"strconv"
	"strings"
)

func BotHandle(w http.ResponseWriter, r *http.Request) {
	bytes, _ := ioutil.ReadAll(r.Body)
	var update Update
	json.Unmarshal(bytes, &update)
	if update.Message == nil {
		return
	}
	botLog := log.WithFields(log.Fields{"chat": update.Message.Chat.ID})
	botLog.Debug("Accept request")
	if isCommand(update.Message.Text, "/start") {
		command := "/start"
		botLog.WithFields(log.Fields{"command": command}).Debug("Start")
		message := "Привет! А тебе точно сюда надо?"
		answerMessage(w, update.Message.Chat.ID, command, message)
		return
	}

	if isCommand(update.Message.Text, "/stop") {
		command := "/stop"
		botLog.WithFields(log.Fields{"command": command}).Debug("Start")
		answerMessage(w, update.Message.Chat.ID, command, "Это ничего не изменит...")
		return
	}

	if isCommand(update.Message.Text, "/help") {
		command := "/help"
		botLog.WithFields(log.Fields{"command": command}).Debug("Start")
		answerMessage(w, update.Message.Chat.ID, command, "Еще не готово")
		return
	}
}

func sendMessage(chatID int64, text string) {
	_, err := http.PostForm(
		"https://api.telegram.org/bot"+config.Token+"/sendMessage",
		url.Values{
			"chat_id": {strconv.FormatInt(chatID, 10)},
			"text":    {text},
		})
	if err != nil {
		log.WithFields(log.Fields{"chat": chatID, "text": text}).Error(err.Error())
	}
}

func answerMessage(w http.ResponseWriter, chatID int64, command, text string) {
	msg := Response{Chatid: chatID, Text: text, Method: "sendMessage"}
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	log.WithFields(log.Fields{"chat": chatID, "command": command}).Debug(text)
	json.NewEncoder(w).Encode(msg)
}

func isCommand(text, command string) bool {
	if strings.Index(text, command) == 0 {
		if strings.Contains(strings.ToLower(text), "@"+strings.ToLower(config.Name)) || !strings.Contains(text, "@") {
			return true
		}
	}
	return false
}
