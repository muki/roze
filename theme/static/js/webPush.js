// check if service workers are available ant start the process or complain
async function registerSw(theP) {
    if ('serviceWorker' in navigator) {
        // show a small loader webpush banner
        console.log(theP);
        theP.innerHTML = '<div class="webpush-loader"></div><p>WebPush notifications are being enabled, you should see an alert in less than a minute.</p><div class="webpush-loader"></div>';
        // register the service worker
        const reg = await navigator.serviceWorker.register('webPush.service.js');
        // do the checks and subscribe the user
        initialiseState(reg);
    } else {
        alert("Your browser does not support the technology needed to make notifications work. :(")
    }
};

// check for notifications and permissions and push manager and complain if things are not fine
const initialiseState = (reg) => {
    if (!reg.showNotification) {
        alert('Showing notifications is not supported in your browser. :(');
        return
    }
    if (Notification.permission === 'denied') {
        alert('You denied the permission to show notifications.');
        return
    }
    if (!'PushManager' in window) {
        alert("WebPush is not supported by your browser. :(");
        return
    }
    subscribe(reg);
}

// unitlity data conversion function
function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    const outputData = outputArray.map((output, index) => rawData.charCodeAt(index));

    return outputData;
}

// function to subscribe
const subscribe = async (reg) => {
    const subscription = await reg.pushManager.getSubscription();
    if (subscription) {
        sendSubData(subscription);
        return;
    }

    const vapidMeta = document.querySelector('meta[name="vapid-key"]');
    const key = vapidMeta.content;
    const options = {
        userVisibleOnly: true,
        // if key exists, create applicationServerKey property
        ...(key && {applicationServerKey: urlB64ToUint8Array(key)})
    };

    const sub = await reg.pushManager.subscribe(options);
    sendSubData(sub)
};

// function to send subscription data to the server
const sendSubData = async (subscription) => {
    const browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase();

    const registration_id = subscription.endpoint;
    const data = {
        p256dh: btoa(
            String.fromCharCode.apply(
            null,
            new Uint8Array(subscription.getKey('p256dh'))
            )
        ),
        auth: btoa(
            String.fromCharCode.apply(
            null,
            new Uint8Array(subscription.getKey('auth'))
            )
        ),
        registration_id: registration_id,
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const res = await fetch('/register_webpush_device/', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'content-type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
    });

    handleResponse(res);
};

// handle server response
const handleResponse = (res) => {
    if (res.status == 200) {
        alert('Your WebPush subscription is confirmed! The app will reload after you close this alert.');
        document.location.reload();
    } else {
        alert('Something went wrong and I do not know what. Consult the person running this website to try and debug your situation.');
    };
};
