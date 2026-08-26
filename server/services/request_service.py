def find_pending_request(sender, receiver, requests):

    for request in requests:
        if(
            request["sender"] == sender
            and request["receiver"] == receiver
            and request["status"] == "pending"
        ):
            return request

    return None



def respond_to_request(sender, reciver, response, requests):

    for request in requests:
        if(
           request["sender"] == sender
            and request["receiver"] == reciver
            and request["status"] == "pending" 
        ):

            if response == "accept":
                request["status"] = "accepted"
                return True
        
            if response == "reject":
                request["status"] = "rejected"
                return True

    return False




def create_request(sender, receiver, requests):

    for request in requests:
        if (
            request["sender"] == sender
            and request["receiver"] == receiver
            and request["status"] == "pending"
        ):

            return False

    requests. append({
        "sender" : sender,
        "receiver" : receiver,
        "status" : "pending"
    })

    return True



def get_requests_for_users(username, requests):

    user_requests = []

    for request in requests:

        if (request["sender"] == username or request["receiver"] == username):

            user_requests.append(request)

    return user_requests



if __name__ == "__main__":
    requests = []

    create_request("Alice", "Bob", requests)
    create_request("Sachin", "John", requests)

    print(find_pending_request("Alice", "Bob", requests))
    print(find_pending_request("Sachin", "John", requests))
    print(find_pending_request("Alice", "John", requests))

    respond_to_request("Alice", "Bob", "accept", requests)

    print(find_pending_request("Alice", "Bob", requests))