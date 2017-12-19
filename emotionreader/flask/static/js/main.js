String.prototype.formattedDT = function() {
    var date = new Date(this);
    var hours = date.getHours();
    var minutes = date.getMinutes();
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes
    // return date.getMonth()+1 + "/" + date.getDate() + "/" + date.getFullYear() + " " + strTime;
    return `${date.getDate()}/${date.getMonth()+1}/${date.getFullYear()} ${strTime}`;
}

let app = {
    pages: [],
    current_page: null,
    current_session: null,
    current_video: null,
    get_page: function(x) {
        if (typeof x == 'number') {
            return this.pages[x];
        }
        else if (typeof x == 'string') {
            return this.pages.find((elem) => {
                return elem.id == x;
            });
        }
        throw new TypeError('invalid identifier given');
    },
    show: function(page, args = null) {
        if (typeof page == 'number' || typeof page == 'string') {
            page = this.get_page(page);
        }

        if (this.current_page) {
            this.current_page.hide();
        }

        args = args || {};
        page.show(args);
        this.current_page = page;
    },
    loadSession: function(session) {
        if (typeof session === 'number') {
            $.get(`/api/session/${session}/`)
                .done((data) => {
                    this.current_session = data;
                    this.show(2);
                })
        } else if (typeof session === 'object') {
            this.current_session = session;
            this.show(2);
        }
    },
    getPersonById: function(id) {
        return app.current_session.users.find(function(elem) {
            return elem.id == id;
        });
    }
};

app.visualization = {
    _emotions: ['anger', 'contempt', 'disgust', 'fear', 'happy',
                'neutral', 'sadness', 'surprise'],
    canvas_list: [],
    name_hidden: true,

    /**
     * Generate a chart from a set of emotions.
     */
    generateSingle: function(emotions, person, avg = false) {
        if (!emotions) return;

        // div.chart-wrapper>span.uk-hidden+canvas
        let div = document.createElement('div');
        if (avg) {
            div.classList.add('chart-wrapper-avg');
        } else {
            div.classList.add('chart-wrapper');
        }

        let name_label = document.createElement('span');
        if (this.name_hidden) {
            name_label.classList.add('uk-hidden', 'name-label');
        } else {
            name_label.classList.add('name-label');
        }
        name_label.innerHTML = person.name;
        div.appendChild(name_label);

        let canvas = document.createElement('canvas');
        div.appendChild(canvas);

        let data = emotions.map((elem) => {
            return (elem * 100).toFixed(2);
        });
        let chart = new Chart(canvas.getContext('2d'), {
            type: 'doughnut',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    display: false
                }
            },
            data: {
                labels: this._emotions,
                datasets: [
                    {
                        data: data,
                        // Color labels:   Anger      Contempt   Disgust    Fear       Happy      Neutral    Sadness    Surprise
                        backgroundColor: ['#DB162F', '#A4036F', '#702632', '#7CB518', '#FFFF00', '#33658A', '#03B5AA', '#FFB400']
                    }
                ]
            }
        });
        this.canvas_list.push(chart);

        document.getElementById('canvas-area').appendChild(div);
        return div;
    },

    _getChartDistance: function(minimum = 280) {
        let dist = window.innerHeight - 670;
        if (dist < minimum) return minimum;
        return dist;
    },

    /**
     * Calculate the coordinates from the center of the div
     * to 200 pixels from the border.
     */
    _calculateCoordinates: function(len, x1, y1, degrees) {
        let rad = degrees * Math.PI / 180;
        x2 = x1 + Math.cos(rad) * len;
        y2 = y1 + Math.sin(rad) * len;
        return {x: x2, y: y2};
    },

    _placeDivAtCoordinates: function(div, coords) {
        let x = coords.x - (div.offsetWidth / 2);
        // the 70 is the pixel height of the top bar
        let y = (coords.y - (div.offsetHeight / 2)) + 70;
        div.style.position = "absolute";
        div.style.top = `${y}px`;
        div.style.left = `${x}px`;
    },

    /**
     * Generate a single frame of charts.
     *
     * One frame is a list containing a list of emotions, in other words
     * the emotions of a single moment in time for a group of people.
     */
    generateFrame: function(frame) {
        this.clear_visual();

        let container = document.getElementById('canvas-area');
        let x_center = container.offsetWidth / 2,
            y_center = container.offsetHeight / 2,
            distance = this._getChartDistance(50),
            degrees = 0;

        let divs = frame.map((elem, index) => { 
            return this.generateSingle(elem, app.getPersonById(this.data[index].person));
        });

        let step = 360 / divs.length;
        for (let i = 0; i < divs.length; i++) {
            this._placeDivAtCoordinates(divs[i], this._calculateCoordinates(distance, x_center, y_center, degrees));
            degrees += step;
        }

        let average = new Array(8).fill(0);
        for (let i = 0; i < frame.length; i++) {
            for (let x = 0; x < frame[i].length; x++) {
                average[x] += frame[i][x];
            }
        }
        let avg_div = this.generateSingle(average, {name: 'Average'}, true);
        this._placeDivAtCoordinates(avg_div, {x: x_center, y: y_center});
    },

    /**
     * Returns the prediction of each video_session instance at a certain timeframe.
     * Can be used to generate the frame of all available video sessions at a given
     * timeframe.
     *
     * Example:
     *     `getTimeFrame(10)` returns the predictions from each person at the 4.5 to 5 second mark.
     *
     * Arguments:
     *     - index: the index of the frame to get.
     */
    getTimeFrame: function(index) {
        let result = [];
        this.data.forEach((elem) => {
            result.push(elem.result[index]);
        });
        return result;
    },

    /**
     * Generate the charts from the current session and video.
     *
     * Arguments:
     *     - data: a list of `VideoSessions`
     */
    generateFromSession: function(data) {
        if (!(data.length > 0)) {
            UIkit.notification({
                message: 'No data to show',
                status: 'warning',
                pos: 'top-right',
                timeout: 3000
            });
            return;
        }

        this.data = data;
        // The video is recorded at 10 FPS, and then the average of 5 frames is taken.
        // Therefore, the amount of predictions in the result list should be `video_length * 2`
        let length = data[0].result.length / 2;
        // the 0th element also counts, so we have to do -0.5 otherwise there would be length+1 elements
        document.getElementById('timeline').max = length - 0.5;

        this.generateFrame(this.getTimeFrame(1));
    },

    clear: function() {
        this.data = null;
        document.getElementById('timeline').max = 0;
        this.clear_visual();
    },
    clear_visual: function() {
        this.canvas_list = [];
        document.getElementById('canvas-area').innerHTML = "";
    },
    toggleNames: function() {
        document.querySelectorAll('span.name-label').forEach((elem) => {
            elem.classList.toggle('uk-hidden');
        });
        app.visualization.name_hidden = !app.visualization.name_hidden;
    }
}

app.pages.push({
    id: 'page_session_picker',
    beforeShow: function(reload) {
        if (reload) {
            this._clearTable();
            $.ajax({
                method: 'GET',
                url: '/api/sessions/',
                contentType: 'application/json'
            })
                .done(function(data){
                    let table = $('#session-table tbody');
                    data.forEach((session) => {
                        table.append(`<tr data-session-id="${session.id}">
                            <td>${session.id}</td>
                            <td>${session.description}</td>
                            <td>${session.user_count}</td>
                            <td>${session.date_created.formattedDT()}</td>
                        </tr>`)
                    });
                });
        }
        this.registerHandlers();
    },
    _clearTable: function() {
        $('#session-table tbody').html('');
    },
    registerHandlers: function() {
        // choose session with table click
        $('#session-table').on('click', 'tr', function() {
            let id = $(this).data('session-id');
            app.loadSession(id);
        });
        // new session button
        $('#btn-new-session').on('click', function() {
            app.show(1);
        });
    },
    beforeHide: function() {
        this.removeHandlers();
    },
    removeHandlers: function() {
        $('#session-table').off('click', 'tr');
        $('#btn-new-session').off('click');
    },
    show: function(args) {
        let reload = args.reload === false ? args.reload : true;
        this.beforeShow(reload);
        document.getElementById(this.id).classList.remove('uk-hidden');
    },
    hide: function() {
        this.beforeHide();
        document.getElementById(this.id).classList.add('uk-hidden');
    }
});

app.pages.push({
    id: 'page_session_creator',
    beforeShow: function() {
        this.registerHandlers();
    },
    registerHandlers: function() {
        /* This event handler is responsible for automatically resizing
         * the amount of participants input fields.
         * Changing the value of the user_count input field, will add
         * or remove the amount of participants
         */
        $('#form-new-session input[name=user_count]').on('change', function() {
            let amount = $(this).val();
            if (amount >= 1 && amount <= 15) {
                let div = $('#form-people-div');
                let num_children = div.children('div').length;
                let diff = Math.abs(amount - num_children);
                if (amount > num_children) {
                    // increase the amount of people input fields
                    for (let i = 0; i < diff; i++) {
                        div.append(
                            `<div class="uk-grid-small" uk-grid>
                                <div class="uk-width-1-2@s">
                                    <input class="uk-input" name="name" placeholder="Name" type="text"/>
                                </div>
                                <div class="uk-width-1-2@s">
                                    <input class="uk-input" name="name" placeholder="Birthdate" type="date"/>
                                </div>
                            </div>`
                        );
                    }
                } else if (amount < num_children) {
                    // shrink the amount of people input fields
                    for (let i = 0; i < diff; i++) {
                        div.children('div').last().remove();
                    }
                }
            }
        });
        $('#btn-session-cancel').on('click', function(e) {
            e.preventDefault();
            app.show(0, {reload: false});
            this.clear();
        }.bind(this));

        $('#btn-session-save').on('click', function(e) {
            e.preventDefault();
            this.saveForm((data) => {
                app.show(0);
                this.clear();
            });
        }.bind(this));

        $('#btn-session-go').on('click', function(e) {
            e.preventDefault();
            this.saveForm((data) => {
                app.loadSession(data);
                this.clear();
            });
        }.bind(this));
    },
    clear: function() {
        // TODO: use jquery :input to iterate over all fields?
        $('#form-new-session input[name=user_count]').val('');
        $('#form-new-session textarea[name=description]').val('');
        $('#form-people-div').html('');
    },
    beforeHide: function() {
        this.removeHandlers();
    },
    removeHandlers: function() {
        $('#btn-session-cancel').off('click');
        $('#btn-session-save').off('click');
        $('#btn-session-go').off('click');
        $('#form-new-session input[name=user_count]').off('change');
    },
    saveForm: function(done) {
        let data = {
            user_count: $('#form-new-session input[name=user_count]').val(),
            description: $('#form-new-session textarea[name=description]').val(),
            users: []
        };
        $('#form-people-div>div').each(function(index, elem) {
            let inputs = $(elem).find(':input');
            data.users.push({
                name: inputs[0].value,
                birthdate: inputs[1].value || null
            })
        });

        $.ajax({
            method: 'PUT',
            contentType: 'application/json',
            url: '/api/sessions/',
            dataType: 'json',
            data: JSON.stringify(data)
        })
        .done(done);
    },
    show: function() {
        this.beforeShow();
        document.getElementById(this.id).classList.remove('uk-hidden');
    },
    hide: function() {
        this.beforeHide();
        document.getElementById(this.id).classList.add('uk-hidden');
    }
});

app.pages.push({
    id: 'page_session_viewer',
    beforeShow: function(reload) {
        if (reload) {
            $('#select-video').html('');
            $('#select-video').append('<option value="-1">-----</option>');
            $.get('/api/videos/')
                .done(function(data) {
                    data.forEach((item) => {
                        $('#select-video').append(
                            `<option value="${item.id}">${item.name}</option>`
                        );
                    })
                });
        }
        this.registerHandlers();
    },
    registerHandlers: function() {
        $('#select-video').on('change', function() {
            app.current_video = $(this).val();
        });

        $('#timeline').on('input', function() {
            let val = parseFloat($(this).val());
            $('#range-output').html(`${val} - ${val + 0.5}`);
        });

        $('#timeline').on('change', function() {
            let index = parseFloat($(this).val()) * 2;
            app.visualization.generateFrame(app.visualization.getTimeFrame(index));
        });

        $('#btn-show-video').on('click', function() {
            if (app.current_video && app.current_session) {
                let url = `/session/${app.current_session.id}/video/${app.current_video}`;
                let win = window.open(url, '_blank');
                if (win) {
                    win.focus();
                }
            } else {
                UIkit.notification({
                    message: 'No video selected',
                    status: 'warning',
                    pos: 'top-right',
                    timeout: 3000
                });
            }
        });
        $('#btn-gen-model').on('click', function() {
            if (app.current_video === "-1") {
                app.visualization.clear();
                return;
            }
            let url = `/api/session/${app.current_session.id}/video/${app.current_video}/video_sessions/`;
            $.get(url).done((data) => { app.visualization.generateFromSession(data); });
        });

        $('#btn-show-names').click(app.visualization.toggleNames);
    },
    show: function(args) {
        let reload = args.reload === false ? args.reload : true;
        this.beforeShow(reload);
        document.getElementById(this.id).classList.remove('uk-hidden');
    },
    hide: function() {
        document.getElementById(this.id).classList.add('uk-hidden');
    }
});

$(document).ready(function() {
    if (window.location.hash.startsWith('#session')) {
        // allow for sessions to be restored easily
        let id = window.location.hash.split('/')[1];
        app.current_session = id;
        app.show(2);
    } else {
        app.show(0);
    }
});
