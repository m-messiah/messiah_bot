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
	updateMessage := update.Message
	if updateMessage == nil {
		if update.EditedMessage == nil {
			return
		}
		updateMessage = update.EditedMessage
	}
	botLog := log.WithFields(log.Fields{"chat": updateMessage.Chat.ID})
	botLog.Debug("Accept request")

	switch {
	case updateMessage.Text != nil:
		if strings.Index(*updateMessage.Text, "/") != 0 {
			handleText(w, updateMessage, botLog)
		} else {
			handleCommand(w, updateMessage, botLog)
		}
	case updateMessage.Sticker != nil:
		handleSticker(w, updateMessage, botLog)
	case updateMessage.Contact != nil:
		handleContact(w, updateMessage, botLog)
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
	msg := Response{Chatid: chatID, Text: &text, Method: "sendMessage"}
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	log.WithFields(log.Fields{"chat": chatID, "command": command}).Debug(text)
	json.NewEncoder(w).Encode(msg)
}
