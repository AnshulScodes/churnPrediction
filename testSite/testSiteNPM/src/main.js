import { ChurnTracker } from 'churn-tracker-sdk'

const tracker = new ChurnTracker({
    apiKey: 'r0ATgJZptfqX5TGhUziMD9GsbsfNZBWNL1DvLKdoVmc',
    apiUrl: 'http://localhost:3000'
});

document.querySelector('#app').innerHTML = `
  <div class="container">
    <h1>Churn Tracker NPM Test</h1>
    <div class="card">
        <button id="initButton">Initialize User</button>
        <button id="trackButton">Track Feature</button>
    </div>
    <pre id="output">// Events will appear here...</pre>
  </div>
`

function log(msg) {
    document.getElementById('output').textContent += '\n' + msg;
}

document.getElementById('initButton').onclick = async () => {
    try {
        const response = await tracker.initUser({
            email: `HAHAHHAHAHAHAHHA@GMAIL.BALLS`,
            planType: 'free'
        });
        log(`User initialized: ${JSON.stringify(response)}`);
    } catch (error) {
        log(`Error: ${error.message}`);
    }
};

document.getElementById('trackButton').onclick = async () => {
    try {
        await tracker.trackFeatureUsage('AHHAFHDKSHFRHFDSKJFHDSKUFHIU');
        log('Feature tracked successfully');
    } catch (error) {
        log(`Error: ${error.message}`);
    }
};