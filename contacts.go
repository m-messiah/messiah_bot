package main

import (
	log "github.com/sirupsen/logrus"
	"net/http"
	"strconv"
)

func handleContact(w http.ResponseWriter, updateMessage *Message, botLog *log.Entry) {
	if updateMessage.Contact.ID != nil {
		botLog.WithFields(log.Fields{"type": "contact", "phone": updateMessage.Contact.Phone}).Debug("Found")
		answerMessage(w, updateMessage.Chat.ID, "contact", strconv.FormatInt(*updateMessage.Contact.ID, 10))
	} else {
		botLog.WithFields(log.Fields{"type": "contact", "phone": updateMessage.Contact.Phone}).Debug("Not found")
		answerMessage(w, updateMessage.Chat.ID, "contact", "Not found in Telegram")
	}
}
