const AsUrl='https://c5.gluu.org';
const clientID='@!82F6.00B8.C20E.272F!0001!DC79.0594!0008!1E13.CB20.2F74.F9BE';


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
    const getUrl = AsAuthUrl + '?response_type=id_token%20token&client_id=' + clientID + '&redirect_uri=' + redirectUri + '&scope=openid%20profile' + '&state=' + state + '&nonce=' + nonce + ' HTTP/1.1';
    window.location.replace(getUrl);

}