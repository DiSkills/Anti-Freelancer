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
        - [x] Update (change)
        - [ ] Delete (by message id **and** sender id)
    - [ ] Get all for dialogue (pagination)
    - [ ] Get all dialogues
    - [ ] Get dialogue
- [ ] Notification
    - [ ] Send email about new message
    - [x] Create (sent)
    - [x] Create (changed)
    - [ ] Create (deleted)
    - [x] Get
    - [x] View (delete)
- [ ] Tests
    - [ ] Message
        - [ ] WebSockets
            - [x] Send
            - [x] Update (change)
    - [ ] Notification
        - [x] Create (sent)
        - [x] Create (changed)
        - [x] Get
        - [x] View (delete)
