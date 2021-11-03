# Messenger Service

## TODO

- [ ] Docker
- [ ] Logger errors in file
- [ ] Permission requests
    - [x] Is authenticated
    - [x] Is active
    - [x] Is superuser
    - [x] Is customer
    - [x] Is freelancer
- [ ] Message
    - [ ] WebSockets
        - [x] Send
        - [ ] Update (by message id **and** sender id)
        - [ ] Delete (by message id **and** sender id)
    - [ ] Get all for dialogue (pagination)
    - [ ] Get all dialogues
    - [ ] Get dialogue
- [ ] Notification
    - [ ] Send email about new message
    - [x] Create (message has been sent)
    - [ ] Create (message has been deleted)
    - [ ] Create (message has been changed)
    - [x] Get
    - [x] View (delete)
- [ ] Tests
    - [ ] Message
        - [ ] WebSockets
            - [x] Send
    - [ ] Notification
        - [x] Create (message has been sent)
        - [x] Get
        - [x] View (delete)
