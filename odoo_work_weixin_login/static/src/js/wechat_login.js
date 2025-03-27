const { ElLoading, ElMessageBox, ElRadioGroup, ElRadioButton } = ElementPlus;

const App = {
    data() {
        return {
            WechatCompanyData: [],
            selectedIndex: 0,
        };
    },

    // 页面加载完成后，DOM已经挂载
    async mounted() {
        let WechatCompanyData = document.querySelector("#wechat_company_data").innerHTML.trim();
        this.WechatCompanyData = JSON.parse(WechatCompanyData.replace(/'/g, '"'));
        if (this.WechatCompanyData.length === 1) {
            this.openWeChartAuthorize(this.WechatCompanyData[0]);
        } else{
            this.showMessageBox();
        }
    },

    methods: {

        showMessageBox() {
            ElMessageBox({
                title: '请选择公司', confirmButtonText: '确定选择',
                type: 'none', 'center': true, showClose: false, roundButton: true,
                message: () => Vue.h(ElRadioGroup, {
                    modelValue: this.selectedIndex, size: 'large',
                    'onUpdate:modelValue': (val) => { this.selectedIndex = val; }
                },
                this.WechatCompanyData.map((item, index) =>
                    Vue.h(ElRadioButton, { label: index }, () => item.name)
                ))
            }).then(() => {
                this.clickCompany();
            }).catch(() => {
                console.log("用户取消选择");
            });
        },

        clickCompany() {
            this.openWeChartAuthorize(this.WechatCompanyData[this.selectedIndex]);
        },

        openWeChartAuthorize(company_data) {
            ElLoading.service({lock: true, text: '正在登录...', background: 'rgba(0, 0, 0, 0.7)'})
            const redirectUrl = encodeURIComponent(window.location.origin + '/wechat/oauth/login');
            const params = `login_type=CorpApp&appid=${company_data['wechat_corp_id']}&agentid=${company_data['wechat_agent_id']}&redirect_uri=${redirectUrl}&state=${company_data['wechat_corp_id']}`
            window.location.replace(`https://login.work.weixin.qq.com/wwlogin/sso/login?${params}`);
        }

    }
}

const app = Vue.createApp(App);
app.use(ElementPlus);
app.mount("#app");
