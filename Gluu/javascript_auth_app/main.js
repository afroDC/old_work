const AsUrl='https://c5.gluu.org';
const clientID='@!82F6.00B8.C20E.272F!0001!DC79.0594!0008!1E13.CB20.2F74.F9BE';
const responseType = 'id_token client_id'
const scopes = 'openid profile email'

function randomString() {
    const validChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let array = new Uint8Array(40);
    window.crypto.getRandomValues(array);
    array = array.map(x => validChars.charCodeAt(x % validChars.length));
    const randomState = String.fromCharCode.apply(null, array);
    return randomState;
}

function implicitAuthRequest(){
    const AsAuthUrl=AsUrl + '/oxauth/restv1/authorize';
    const redirectUri='http://localhost:8080/success';
    let state = randomString();
    let nonce = randomString();
    // const getUrl = AsAuthUrl + '?response_type=id_token%20token&client_id=' + clientID + '&redirect_uri=' + redirectUri + '&scope=openid%20profile' + '&state=' + state + '&nonce=' + nonce;
    const getUrl = AsAuthUrl + '?response_type=' + responseType + '&client_id=' + clientID + '&redirect_uri=' + redirectUri + '&scope=' + scopes + '&state=' + state + '&nonce=' + nonce;
    // Store nonce and state
    window.sessionStorage.setItem("nonce", nonce);
    window.sessionStorage.setItem("state", state);
    // Redirect for Implicit Flow
    window.location.replace(getUrl);
}

function parseJwt (token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    decoded = atob(base64);
    parsed = JSON.parse(decoded);
    return parsed;
};

function parseUrl () {
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
    // Realistically, in a production application, we would want to cache this in redis.
    window.sessionStorage.setItem("authResp", JSON.stringify(params));
}

function postAuthRedirect () {
    // Parse the current URL and store the information into browser cache.
    parseUrl();
    // Gather our authentication response to verify
    var response = JSON.parse(window.sessionStorage.getItem("authResp"));
    accessToken = response.access_token;
    // Base64 Decode the id_token
    idToken64 = response.id_token;
    idToken = parseJwt(idToken64);
    // Verify nonce, audience, response type and issuer
    appNonce = window.sessionStorage.getItem('nonce');
    if (idToken['iss'] == AsUrl && appNonce == idToken['nonce'] && clientID == idToken['aud']) {
        window.sessionStorage.setItem("session_id", response.session_id);
        window.location.replace("http://localhost:8080");
    }
    else {
        alert("Nonce, Issuer or Audience didn't match. Session invalid per spec.")
    }
}

function logout () {
    // Front end logout and end current session.
    alert("Logging out.")
    var response = JSON.parse(window.sessionStorage.getItem("authResp"));
    alert(response);
    idToken64 = response.id_token;
    const postLogoutUri = 'http://localhost:8080/'
    const getUrl = AsUrl + '?id_token_hint=' + idToken64 + '&post_logout_redirect_uri=' + postLogoutUri;
    alert(getUrl);
    window.location.replace(getUrl);
}