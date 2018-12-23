package main

type Config struct {
	Port     int64
	LogLevel string
	Name     string
	Admins   map[string]string
	Token    string
	Devices  map[string]Device
}

type Device struct {
	MacAddr string
}

// Response to Telegram
type Response struct {
	Chatid  int64   `json:"chat_id"`
	Text    *string `json:"text"`
	Sticker *string `json:"sticker"`
	Method  string  `json:"method"`
}

// Chat Telegram structure
type Chat struct {
	ID       int64
	Username *string
}

// MessageEntity Telegram structure
type MessageEntity struct {
	Type   string
	Offset int64
	Length int64
}

// Sticker Telegram structure
type Sticker struct {
	FileID string `json:"file_id"`
	Emoji  string
}

// Contact Telegram structure
type Contact struct {
	ID       *int64  `json:"user_id"`
	LastName *string `json:"last_name"`
	Name     string  `json:"first_name"`
	Phone    string  `json:"phone_number"`
}

// Message Telegram structure
type Message struct {
	Chat     *Chat
	Contact  *Contact
	Entities *[]MessageEntity
	Sticker  *Sticker
	Text     *string
}

// Update - outer Telegram structure
type Update struct {
	Message       *Message
	EditedMessage *Message `json:"edited_message"`
}

type MACAddress [6]byte

type MagicPacket struct {
	header  [6]byte
	payload [16]MACAddress
}
