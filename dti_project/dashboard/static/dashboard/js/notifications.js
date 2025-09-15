document.addEventListener('DOMContentLoaded', function() {
    const bellIcon = document.querySelector('.header-notifications .fa-bell');
    const notificationsContainer = document.querySelector('.notifications-container');
    const suggestionsBox = document.getElementById('suggestions-box');
    const notificationsList = document.querySelector('.notifications-list');

    // --- Notification sound setup ---
    const notificationSound = new Audio("/static/dashboard/sounds/What%20The%20Hell%20Meme%20Sound%20Effect.mp3");
    notificationSound.volume = 0.3; // subtle volume
    let audioUnlocked = false;
    let queuedNotifications = 0;

    // Unlock audio on first subtle interaction
    function unlockAudio() {
        if (!audioUnlocked) {
            audioUnlocked = true;
            console.log("Notification sound unlocked!");
            // Play all queued notifications
            for (let i = 0; i < queuedNotifications; i++) {
                notificationSound.play().catch(err => console.log("Sound play failed:", err));
            }
            queuedNotifications = 0;
        }
    }
    window.addEventListener('mousemove', unlockAudio, { once: true });
    window.addEventListener('scroll', unlockAudio, { once: true });
    window.addEventListener('keydown', unlockAudio, { once: true });

    // --- Dropdown toggle ---
    if (bellIcon && notificationsContainer) {
        bellIcon.addEventListener('click', () => {
            notificationsContainer.classList.toggle('visible');
            if (suggestionsBox && suggestionsBox.classList.contains('visible')) {
                suggestionsBox.classList.remove('visible');
            }
        });
    }

    // --- Auto-hide when suggestions box is visible ---
    if (suggestionsBox) {
        const observer = new MutationObserver(() => {
            if (suggestionsBox.style.visibility === 'visible') {
                notificationsContainer.classList.remove('visible');
            }
        });
        observer.observe(suggestionsBox, { attributes: true, attributeFilter: ['style'] });
    }

    // --- Click outside to close ---
    document.addEventListener('click', function(e) {
        if (!bellIcon.contains(e.target) && !notificationsContainer.contains(e.target)) {
            notificationsContainer.classList.remove('visible');
        }
    });

    // --- WebSocket setup ---
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const socketUrl = protocol + window.location.host + '/ws/notifications/';
    const notificationSocket = new WebSocket(socketUrl);

    // --- Handle incoming notifications ---
    notificationSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        // Update bell counter
        if (bellIcon) {
            let count = parseInt(bellIcon.dataset.count || "0", 10) + 1;
            bellIcon.dataset.count = count;
            bellIcon.setAttribute("data-count", count);
        }

        // Play sound immediately if unlocked, else queue
        if (audioUnlocked) {
            notificationSound.play().catch(err => console.log("Sound play failed:", err));
        } else {
            queuedNotifications++;
        }

        // Prepend new notification item to list
        const li = document.createElement("li");
        li.innerHTML = `
            <div class="system-icon"><i class="fa-solid fa-cog"></i></div>
            <div class="details">
                <div class="row">${data.message}</div>
                <p class="time-since">Just now</p>
            </div>
        `;
        if (notificationsList) notificationsList.prepend(li);
    };

    notificationSocket.onclose = function(e) {
        console.error("Notification socket closed unexpectedly");
    };
});
