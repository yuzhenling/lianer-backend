/ 创建WebSocket连接（需要包含用户认证信息）
const ws = new WebSocket('ws://your-server/tuner/ws/analyze', {
    headers: {
        'Authorization': 'Bearer your-jwt-token'
    }
});

// 连接建立时的处理
ws.onopen = () => {
    console.log('Connected to server');
    startAudioCapture();
};

// 接收分析结果
ws.onmessage = (event) => {
    const result = JSON.parse(event.data);
    console.log('Analysis result:', result);
    updateTunerUI(result);
};

// 连接关闭时的处理
ws.onclose = () => {
    console.log('Disconnected from server');
    stopAudioCapture();
};

// 音频采集函数
function startAudioCapture() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            const audioContext = new AudioContext();
            const source = audioContext.createMediaStreamSource(stream);
            const processor = audioContext.createScriptProcessor(4096, 1, 1);

            source.connect(processor);
            processor.connect(audioContext.destination);

            processor.onaudioprocess = (e) => {
                const audioData = e.inputBuffer.getChannelData(0);
                // 将音频数据发送到服务器
                ws.send(audioData);
            };
        })
        .catch(err => console.error('Error accessing microphone:', err));
}

// 停止音频采集
function stopAudioCapture() {
    // 停止音频采集的逻辑
}

// 更新UI的函数
function updateTunerUI(result) {
    // 更新调音器UI的逻辑
    document.getElementById('note').textContent = result.detected_note;
    document.getElementById('frequency').textContent = result.frequency.toFixed(2);
    document.getElementById('cents').textContent = result.cents_difference.toFixed(2);
    document.getElementById('status').textContent = result.tuning_status;
    document.getElementById('direction').textContent = result.tuning_direction;
}