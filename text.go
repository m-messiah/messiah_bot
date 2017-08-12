package main

import (
	log "github.com/sirupsen/logrus"
	"net/http"
)

func handleText(w http.ResponseWriter, updateMessage *Message, botLog *log.Entry) {
	answerMessage(w, updateMessage.Chat.ID, "None", "Я пока умею только команды")
}
