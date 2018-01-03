//GoroupMeBot
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	//"strings"
	//"io/ioutil"
	"time"
)

type GroupMessagesResponseWrapper struct {
	Response GroupMessagesResponse  `json:"response"`
	Meta     map[string]interface{} `json:"meta"`
}

type GroupMessagesResponse struct {
	Count    int              `json:"count"`
	Messages []GroupMeMessage `json:"messages"`
}

type GroupMeMessage struct {
	Attachments []GroupMeMessageAttachment `json:"attachments"`
	AvatarURL   string                     `json:"avatar_url"`
	CreatedAt   int                        `json:"created_at"`
	FavoritedBy []string                   `json:"favorited_by"`
	GroupID     string                     `json:"group_id"`
	ID          string                     `json:"id"`
	Name        string                     `json:"name"`
	SenderID    string                     `json:"sender_id"`
	SenderType  string                     `json:"sender_type"`
	SourceGUID  string                     `json:"source_guid"`
	System      bool                       `json:"system"`
	Text        string                     `json:"text"`
	UserID      string                     `json:"user_id"`
}

type GroupMeMessageAttachment struct {
	Type    string   `json:"type"`
	UserIDs []string `json:"user_ids"`
	Loci    [][]int  `json:"loci"`
	URL     string   `json:"url"`
}

type GroupInfoResponseWrapper struct {
	Response GroupInfoResponse      `json:"response"`
	Meta     map[string]interface{} `json:"meta"`
}

type GroupInfoResponse struct {
	GroupID     string          `json:"group_id"`
	Name        string          `json:"name"`
	Description string          `json:"description"`
	ImageURL    string          `json:"image_url"`
	Members     []GroupMeMember `json:"members"`
}

type GroupMeMember struct {
	UserID    string `json:"user_id"`
	ID        string `json:"id"`
	Name      string `json:"nickname"`
	AvatarURL string `json:"image_url"`
}

var myClient = &http.Client{Timeout: 10 * time.Second}

func getGroupMembers(url string) {

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		fmt.Println(err)
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		fmt.Println(err)
	}
	defer resp.Body.Close()

	decoder := json.NewDecoder(resp.Body)

	var data GroupInfoResponseWrapper
	err = decoder.Decode(&data)
	if err != nil {
		fmt.Printf("%T\n%s\n%#v\n", err, err, err)
	}

	for i, mem := range data.Response.Members {
		fmt.Printf("%d: %s %s\n", i, mem.UserID, mem.Name)
	}
}

// Used to gather all messages from GroupMe
// Still need to build a function to save all these messages to file.
func saveAllMessages(url string) {

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		fmt.Println(err)
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		fmt.Println(err)
	}
	defer resp.Body.Close()

	decoder := json.NewDecoder(resp.Body)

	var data GroupMessagesResponseWrapper
	err = decoder.Decode(&data)

	jsonMess, err := json.Marshal(data)
	//err = ioutil.WriteFile("allMessages.json", jsonMess, 0644)
	f, err := os.OpenFile("allMessages.json", os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0600)
	if err != nil {
		fmt.Printf("%T\n%s\n%#v\n", err, err, err)
	}
	defer f.Close()

	if _, err = f.Write(jsonMess); err != nil {
		panic(err)
	}
	// Iterate through the 100 message limit by utilizing before_id of the last message id in the request.
	for i, mes := range data.Response.Messages {

		//fmt.Printf("%d: %s %s %s\n", i, mes.Name, mes.Text, mes.ID)
		if ln := len(data.Response.Messages); i == ln-1 {
			//fmt.Println("Last message id: ", mes.ID)
			saveAllMessages("https://api.groupme.com/v3/groups/9672911/messages?token=03Y3Q6VCHem5jGABvaPnZHEBN7ipxPHdTiEKbxL2&limit=100" + "&before_id=" + mes.ID)
		}

	}

}

func getJson(url string, target interface{}) error {
	req, err := myClient.Get(url)
	if err != nil {
		return err
	}
	defer req.Body.Close()

	return json.NewDecoder(req.Body).Decode(target)
}

func exampleGet() {
	groupID := "9672911"
	token := "03Y3Q6VCHem5jGABvaPnZHEBN7ipxPHdTiEKbxL2"
	wrapper := &GroupMessagesResponseWrapper{}
	getJson("https://api.groupme.com/v3/groups/"+groupID+"/messages?token="+token+"&limit=100", wrapper)
	fmt.Println(wrapper.Response.Messages)
}

func main() {
	//groupUrl := "https://api.groupme.com/v3/groups/9672911"
	messageUrl := "https://api.groupme.com/v3/groups/9672911/messages?token=03Y3Q6VCHem5jGABvaPnZHEBN7ipxPHdTiEKbxL2&limit=100"

	//getGroupMembers(groupUrl)

	saveAllMessages(messageUrl)


}
