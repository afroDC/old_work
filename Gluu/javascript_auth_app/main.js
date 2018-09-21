const AsUrl = 'https://c5.gluu.org';
const clientID = '@!82F6.00B8.C20E.272F!0001!DC79.0594!0008!1E13.CB20.2F74.F9BE';
const responseType = 'id_token token'
const scopes = 'openid profile email'

// Utilities //

function randomString() {
    // Create unique identifiers for state and nonce.
    const validChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let array = new Uint8Array(40);
    window.crypto.getRandomValues(array);
    array = array.map(x => validChars.charCodeAt(x % validChars.length));
    const randomState = String.fromCharCode.apply(null, array);
    return randomState;
}

function parseJwt (token) {
    // Parse the Base 64 encoded ID Token from the authorization response.
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    decoded = atob(base64);
    parsed = JSON.parse(decoded);
    return parsed;
}

function parseUrl () {
    // Gather current URL
    var url = window.location.href;
    url = url.substring(1);
    var params = {}, responses, temp, i, l;
    // Split into key/value pairs
    url = url.split('#').pop();
    responses = url.split("&");
    // Convert the array of strings into an object
    for ( i = 0, l = responses.length; i < l; i++ ) {
        temp = responses[i].split('=');
        params[temp[0]] = temp[1];
    }
    // Store certain params, like ID Token, scope, etc in a "database" and store session_state in a cookie.
    window.localStorage.setItem("authResp", JSON.stringify(params));
    setCookie("session_state",params.session_state,1);
}

function setCookie(cname,cvalue,exdays) {
    // Create cookie to store session state from authorization response.
    var d = new Date(); //Create a date object
    d.setTime(d.getTime() + (exdays*1000*60*60*24)); //Set the time to exdays from the current date in milliseconds. 1000 milliseonds = 1 second
    var expires = "expires=" + d.toGMTString(); //Compose the expiration date
    window.document.cookie = cname + "=" + cvalue + "; " + expires + "; path=/"; //Set the cookie with value and the expiration date
}

function getCookieValue(cookieName) {
    var name = cookieName + "=";
    var cookies = document.cookie.split(';');
    if (!cookies) {
              return null;
    }
    for (var i = 0; i < cookies.length; i++) {
              var cookie = cookies[i].trim();
              if (cookie.indexOf(name) == 0) {
                        return cookie.substring(name.length, cookie.length);
              }
    }
    return null;
}

function parseJsonResponseForHtml (jsonobject) {
    var output = '';
    var obj = jsonobject;
    for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
            output = output + key + ' : ' + obj[key] + '<br />';
        }
    }
    return output;
}

// Session Management //

function startChecking() {
    checkSessionStatus();
    // Check status every 60 seconds
    setInterval("checkSessionStatus()", 1000*60);
}

function checkSessionStatus () {
    // Display session status on "/"" and also intermittently check that the users Gluu Server session is still valid
    var sessionState = getCookieValue("session_state");
    var mes = clientID + " " + sessionState;
    var iframe = document.getElementById("iframeOP");
    iframe.contentWindow.postMessage(mes, "https://c5.gluu.org");
    window.addEventListener("message", receiveOPMessage, false);
}

function receiveOPMessage (event) {
    if (event.origin !== AsUrl) {
        alert("Origin did not come from the OP; this message must be rejected")
        return;
    }
    if (event.data === "unchanged") {
            // User is still logged in to the OP
            // Do nothing
            document.getElementById("login_status").innerHTML = "Logged In."
    } else {
            // User has logged out of the OP
            // Take some action to attempt refreshing session or forcing user/client to re-auth
            document.getElementById("login_status").innerHTML = "Logged Out."
    }
}

function logout () {
    // End current local application session.
    var response = JSON.parse(window.localStorage.getItem("authResp"));
    idToken64 = response.id_token;
    const postLogoutUri = 'http://localhost:8080/finish_logout'
    const getUrl = AsUrl + '/oxauth/restv1/end_session' + '?post_logout_redirect_uri=' + postLogoutUri;
    document.cookie = "session_state=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    window.location.replace(getUrl);
    window.localStorage.removeItem("authResp");
}

// Authentication //

function implicitAuthRequest(){
    const AsAuthUrl=AsUrl + '/oxauth/restv1/authorize';
    const redirectUri='http://localhost:8080/success';
    let state = randomString();
    let nonce = randomString();
    // Auth requested formatted as such according to https://openid.net/specs/openid-connect-core-1_0.html#ImplicitAuthRequest
    const getUrl = AsAuthUrl + '?response_type=' + responseType + '&client_id=' + clientID + '&redirect_uri=' + redirectUri + '&scope=' + scopes + '&state=' + state + '&nonce=' + nonce;
    // Store nonce and state
    window.localStorage.setItem("nonce", nonce);
    setCookie("state", state, 1);
    // Redirect for Implicit Flow
    window.location.replace(getUrl);
}

function validate (issuer, nonce, audience) {

    // Should fully validate based off of OpenID Connect Core 3.2.2.8. Authentication Response Validation
    // 3.2.2.9. Access Token Validation and 3.2.2.11. ID Token Validation

    appNonce = window.localStorage.getItem('nonce');

    if (issuer != AsUrl) {
        alert("Issuer does not match.");
        // Redirect to attempt to login agai.
        return;
    }
    if (nonce != appNonce) {
        alert("Nonce does not match.");
        // Redirect to attempt to login again.
        return;
    }
    if (audience != clientID) {
        alert("Client ID does not match.");
        // Redirect to attempt to login again.
        return;
    }
    return true;
}

function postAuthRedirect () {
    // Gather our authentication response to verify
    var response = JSON.parse(window.localStorage.getItem("authResp"));
    // Base64 Decode the id_token
    idToken64 = response.id_token;
    idToken = parseJwt(idToken64);
    // Verify nonce, audience, response type and issuer
    if (validate(idToken['iss'], idToken['nonce'], idToken['aud'])) {
        window.location.replace("http://localhost:8080/");
    }
    else {
        document.getElementById("passFail").innerHTML = "Failed to validate response!";
    }
}

function gatherUserClaims () {
    authData = JSON.parse(window.localStorage.getItem('authResp'));
    accessToken = authData.access_token;
    url = AsUrl + '/oxauth/restv1/userinfo';
    var http = new XMLHttpRequest();
    http.onreadystatechange = function() {     
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("user_claims").innerHTML = parseJsonResponseForHtml(JSON.parse(this.responseText));
        }
        else {
            document.getElementById("user_claims").innerHTML = parseJsonResponseForHtml(JSON.parse(this.responseText));
        }
    };
    http.open("GET", url);
    http.setRequestHeader('Authorization','Bearer ' + accessToken);
    http.send();
}
