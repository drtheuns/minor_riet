$(document).ready(function() { app = { video: document.getElementById('video'),
        user: $('#user-select').val() || null,
        is_ready: false,
        has_watched: false,  // Prevent double plays in a row (override by changing selected user)

        set ready(val) {
            $('#user-select').prop('disabled', val);
            this.is_ready = val;
        },

        get ready() {
            return this.is_ready;
        },

        set current_user(val) {
            this.has_watched = false;
        },

        get current_user() {
            return this.user;
        },

        videoFullscreen: function() {
            if (this.video.requestFullscreen) {
                this.video.requestFullscreen();
            }
        },

        play: function() {
            if (this.has_watched) {
                UIkit.notification({
                    message: 'You have already watched the video.',
                    status: 'warning',
                    pos: 'top-right',
                    timeout: 3000
                });
                return;
            }

            let url = `/api/action/record/${session_id}/${video_id}/${this.current_user}/`;
            $.get(url)
                .done(function() {
                    $('#control-overlay').hide();
                    app.video.play();
                })
        }
    };

    $('#user-select').change(function() {
        app.current_user = $(this).val();
    });

    $('#btn-ready').click(function() {
        app.ready = true;
        app.videoFullscreen();
    });

    $('#video').on('ended', function() {
        app.has_watched = true;
        $('#control-overlay').show();
        app.ready = false;
    });

    $(document).keydown(function(e) {
        if ((e.keyCode === 0 || e.keyCode === 32) && app.ready) {
            e.preventDefault();
            app.play();
        }
    });
});
