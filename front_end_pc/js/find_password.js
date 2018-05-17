var vm = new Vue({
    el: '#app',
    data: {
        host: host,

        image_code_id: '',
        image_code_url: '',

        username: '',
        image_code: '',
        mobile: '',
        access_token: '',
        sms_code: '',
        user_id: '',
        password: '',
        password2: '',

        // 发送短信的标志
        sending_flag: false,

        error_username: false,
        error_image_code: false,
        error_sms_code: false,

        error_username_message: '',
        error_image_code_message: '',
        sms_code_tip: '获取短信验证码',
        error_sms_code_message: '',
        error_password: false,
        error_check_password: false,

        // 控制表单显示
        is_show_form_1: true,
        is_show_form_2: false,
        is_show_form_3: false,
        is_show_form_4: false,

        // 控制进度条显示
        step_class: {
            'step-1': true,
            'step-2': false,
            'step-3': false,
            'step-4': false
        },
    },
    created: function(){
        this.generate_image_code();
    },
    methods: {
        // 生成uuid
        generate_uuid: function(){
            var d = new Date().getTime();
            if(window.performance && typeof window.performance.now === "function"){
                d += performance.now(); //use high-precision timer if available
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = (d + Math.random()*16)%16 | 0;
                d = Math.floor(d/16);
                return (c =='x' ? r : (r&0x3|0x8)).toString(16);
            });
            return uuid;
        },
        // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
        generate_image_code: function(){
            // 生成一个编号
            // 严格一点的使用uuid保证编号唯一， 不是很严谨的情况下，也可以使用时间戳
            this.image_code_id = this.generate_uuid();

            // 设置页面中图片验证码img标签的src属性
            this.image_code_url = this.host + "/image_codes/" + this.image_code_id + "/";
        },
        // 检查数据
        check_username: function(){
            if (!this.username) {
                this.error_username_message = '请填写用户名或手机号';
                this.error_username = true;
            } else {
                this.error_username = false;
            }
        },
        check_image_code: function(){
            if (!this.image_code) {
                this.error_image_code_message = '请填写验证码';
                this.error_image_code = true;
            } else {
                this.error_image_code = false;
            }
        },
        check_sms_code: function(){
            if(!this.sms_code){
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },

        // 第一步表单提交, 获取手机号与发送短信的token
        form_1_on_submit: function(){
            this.check_username();
            this.check_image_code();

            if (this.error_username == false && this.error_image_code == false) {
                axios.get(this.host+'/accounts/' + this.username + '/sms/token/?text='+ this.image_code + '&image_code_id=' + this.image_code_id, {
                        responseType: 'json'
                    })
                    .then(response => {
                        this.mobile = response.data.mobile;
                        this.access_token = response.data.access_token;
                        this.step_class['step-2'] = true;
                        this.step_class['step-1'] = false;
                        this.is_show_form_1 = false;
                        this.is_show_form_2 = true;
                    })
                    .catch(error => {
                        if (error.response.status == 400) {
                            this.error_image_code_message = '验证码错误';
                            this.error_image_code = true;
                        } else if (error.response.status == 404) {
                            this.error_username_message = '用户名或手机号不存在';
                            this.error_username = true;
                        } else {
                            console.log(error.response.data);
                        }
                    })
            }
        },

        // 第二步
        // 发送短信验证码
        send_sms_code: function(){

        },
        // 第二步表单提交，验证手机号，获取修改密码的access_token
        form_2_on_submit: function(){

        },

        // 第三步
        check_pwd: function (){

        },
        check_cpwd: function (){

        },
        form_3_on_submit: function(){

        }
    }
})