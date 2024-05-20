import flet as ft
import pandas as pd
import argparse
import time, datetime

# theme_style=ft.TextThemeStyle.DISPLAY_LARGE
jst_standard = datetime.timezone(datetime.timedelta(hours=9), 'JST')

class DataProvider(object):
    def __init__(self, csv, random=False):
        self.csv = csv
        self.counter = 0
        self.df = pd.read_csv(csv)
        if random is True:
            self.df = self.df.sample(frac=1)

    def __iter__(self):
        return self

    def __length__(self):
        return len(self.df)
    
    def __next__(self):
        if self.counter == len(self.df):
            raise StopIteration()
        
        row = self.df.iloc[self.counter]
        self.counter += 1

        return row['key'], row['path']
    
    def remind(self):
        return len(self.df) - self.counter   

trial_data_provider = None
test_data_provider = None
#speaker_data_provider = None
eval_dict = {'eval':[], 'key': [], 'value1': [], 'value2': [], 'start_time': [], 'end_time1': [], 'end_time2': [], 'path': []}

class TopView(ft.View):
    def __init__(self):
        global test_data_provider, trial_data_provider
        controls = [
            ft.Text(spans=[
                    ft.TextSpan(
                        'これから聴取実験を行います。',
                    )
                ]
            ),
            ft.Text("　"),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '実験では、さまざまな人が文章を読み上げた音声がスピーカーから流れます。',
                    )
                ]
            ),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '実験参加者のあなたは、聞き取った音声の明瞭度と自然さを評価します。　　',
                    )
                ]
            ),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '聞き取り音声は全部で',
                    ),
                    ft.TextSpan(
                        str(test_data_provider.__length__()),
                        ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    ),
                    ft.TextSpan(
                        '文あります。',
                    )
                ]
            ),
            ft.Text("　"),
            ft.Text('準備ができたら「次へ」をクリックして進みます。'),
            ft.ElevatedButton(content=ft.Text('次へ'), on_click=self.clicked)
        ]
        super().__init__("/", controls=controls)
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

    def clicked(self, e):
        e.page.go("/trialview")

class IntermView(ft.View):
    def __init__(self):
        #global speaker_data_provider
        controls = [
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '次から本番になります。'
                    )
                ]
            ),
            ft.Text('　'),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '聞き取りは'
                    ),
                    ft.TextSpan(
                        '１回しかできませんので',
                        ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    ),
                    ft.TextSpan(
                        '、注意してください。　　　　　　　　　　　'
                    )
                ]
            ),
            ft.Text('　'),
            ft.Text('準備ができたら「次へ」をクリックして始めます。'),
            ft.ElevatedButton(content=ft.Text('次へ'), on_click=self.clicked)
        ]
        super().__init__("/", controls=controls)
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

    def clicked(self, e):
        e.page.go("/testview")

class LastView(ft.View):
    def __init__(self, path):
        controls = [
            ft.Text('聴取実験は終わりです'),
            ft.Text('おつかれさまでした')
        ]
        super().__init__("/lastview", controls=controls)
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

        global eval_dict
        output_df = pd.DataFrame.from_dict(eval_dict, orient='columns')
        output_df.to_csv(path, index=False)

class TestViewBase(ft.View):
    def __init__(self, key, path):
        self.play_inst = ft.Text('「再生」をクリックして音声を聞き取ってください。')
        self.playb = ft.ElevatedButton(content=ft.Text("再生"), 
                                       on_click=lambda _: self.audio.play(), 
                                       disabled=True)
        self.playb.padding = ft.padding.only(top=50, bottom=100)        
        self.audio, self.opinion1, self.opinion2 = self.setup(path)
        self.inst1 = ft.Text('明瞭度に関して次の5段階で評価してください。', 
                            color=ft.colors.GREY_50)
        self.inst1.padding=ft.padding.only(top=50)
        #self.opinion.padding = ft.padding.only(left=1024, bottom=50)
        self.opinion1.padding = ft.padding.only(left=256, bottom=50)
        self.inst2 = ft.Text('自然さに関して次の5段階で評価してください。', 
                            color=ft.colors.GREY_50)
        self.inst2.padding=ft.padding.only(top=50)
        self.opinion2.padding = ft.padding.only(left=256, bottom=50)
        self.nextb = ft.ElevatedButton(content=ft.Text('次へ'), 
                                       on_click=self.clicked,
                                       disabled=True)
        self.nextb.padding = ft.padding.only(top=100)
        self.nextm = ft.Text('評価が終わったら「次へ」をクリックして進みます。', color=ft.colors.WHITE)

        self.key = key
        self.path = path
        self.value1 = self.value2 = None
        self.start_time = None
        self.end_time1 = self.end_time2 = None

    def setup(self, src):
        audio = ft.Audio(src=src, volume=1, balance=0, 
                         on_state_changed=self.state_changed,
                         on_loaded=self.activate_play_button,
                         autoplay=False)
        self.radio1_1 = ft.Radio(value="5", label="よくわかる", disabled=True )
        self.radio1_2 = ft.Radio(value="4", label="ときどきわからない語がある", disabled=True)
        self.radio1_3 = ft.Radio(value="3", label="聞き手が話題を知っていればわかる", disabled=True)
        self.radio1_4 = ft.Radio(value="2", label="ときどきわかる語がある", disabled=True)
        self.radio1_5 = ft.Radio(value="1", label="全くの了解不能", disabled=True)
        opinion1 = ft.Container(content=ft.RadioGroup(content=ft.Column([
            self.radio1_1, self.radio1_2, self.radio1_3, self.radio1_4, self.radio1_5
        ]), on_change=self.value_changed1))
        self.radio2_1 = ft.Radio(value="5", label="全くの自然である（不自然な要素がない）", disabled=True )
        self.radio2_2 = ft.Radio(value="4", label="やや不自然な要素がある", disabled=True)
        self.radio2_3 = ft.Radio(value="3", label="明らかに不自然である", disabled=True)
        self.radio2_4 = ft.Radio(value="2", label="顕著に不自然である", disabled=True)
        self.radio2_5 = ft.Radio(value="1", label="全く不自然である（自然な要素がない）", disabled=True)
        self.radio2_6 = ft.Radio(value="0", label="内容を理解できず，評価できない", disabled=True)
        opinion2 = ft.Container(content=ft.RadioGroup(content=ft.Column([
            self.radio2_1, self.radio2_2, self.radio2_3, self.radio2_4, self.radio2_5, self.radio2_6
        ]), on_change=self.value_changed2))
        return audio, opinion1, opinion2
    
    def state_changed(self, e):
        if e.data == 'completed':
            self.inst1.color=ft.colors.BLACK
            self.inst1.update()
            self.inst2.color=ft.colors.BLACK
            self.inst2.update()
            self.radio1_1.disabled=False
            self.radio1_1.update()
            self.radio1_2.disabled=False
            self.radio1_2.update()
            self.radio1_3.disabled=False
            self.radio1_3.update()
            self.radio1_4.disabled=False
            self.radio1_4.update()
            self.radio1_5.disabled=False
            self.radio1_5.update()
            self.radio2_1.disabled=False
            self.radio2_1.update()
            self.radio2_2.disabled=False
            self.radio2_2.update()
            self.radio2_3.disabled=False
            self.radio2_3.update()
            self.radio2_4.disabled=False
            self.radio2_4.update()
            self.radio2_5.disabled=False
            self.radio2_5.update()
            self.radio2_6.disabled=False
            self.radio2_6.update()

    def clicked(self, e):
        raise NotImplementedError()

    def value_changed1(self, e):
        self.value1 = e.data
        #self.nextm.color=ft.colors.BLACK
        #self.nextm.update()
        global jst_standard
        self.end_time1 = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
    
    def value_changed2(self, e):
        self.value2 = e.data
        self.nextb.disabled = False
        self.nextb.update()
        self.nextm.color=ft.colors.BLACK
        self.nextm.update()
        global jst_standard
        self.end_time2 = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]

    def activate_play_button(self, e):
        self.playb.disabled=False
        self.playb.update()

class TestView(TestViewBase):
    def __init__(self, key, path):
        
        super().__init__(key, path)
        global test_data_provider
        self.q_number = ft.Text("No." + str(test_data_provider.counter) + " of " + str(test_data_provider.__length__()))
        self.q_number.padding = ft.padding.only(bottom=100)

        controls = [
            self.q_number,
            self.play_inst,
            self.playb,
            self.audio,
            self.inst1,
            self.opinion1,
            self.inst2,
            self.opinion2,
            #self.reminder,
            self.nextm,
            self.nextb
        ]

        #time.sleep(1)
        super(TestViewBase, self).__init__("/testview", controls=controls)
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

    def state_changed(self, e):
        super().state_changed(e)
        if e.data == 'completed':
            #self.inst.color=ft.colors.BLACK
            #self.inst.update()
            global jst_standard
            self.start_time = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
        elif e.data == 'playing':
            self.playb.disabled=True
            self.playb.update()

    def clicked(self, e):
        global test_data_provider, eval_dict
        eval_dict['eval'].append('test')
        eval_dict['key'].append(self.key)
        eval_dict['value1'].append(self.value1)
        eval_dict['value2'].append(self.value2)
        eval_dict['start_time'].append(self.start_time)
        eval_dict['end_time1'].append(self.end_time1)
        eval_dict['end_time2'].append(self.end_time2)
        eval_dict['path'].append(test_data_provider.csv)

        try:
            key, path = test_data_provider.__next__()
            e.page.views.pop()
            e.page.views.append(TestView(key, path))
            e.page.update()
        except StopIteration:
            e.page.go('/lastview')


class TrialView(TestViewBase):
    def __init__(self, key, path):
        
        super().__init__(key, path)
        global trial_data_provider
        self.q_number = ft.Text("No." + str(trial_data_provider.counter) + " of " + str(trial_data_provider.__length__()))
        self.q_number.padding = ft.padding.only(bottom=100)
        self.add_inst1 = ft.Text('まず，聴取する音を再生します．1回しか再生しないので注意してください．',
                                color=ft.colors.RED)
        self.add_inst2 = ft.Text('再生が終わったら，いま聴取した音を評価します．',
                                color=ft.colors.WHITE)
        self.add_inst2.padding=ft.padding.only(top=200)

        #self.reminder = ft.Text("残り：" + str(trial_data_provider.remind()) + "/" + str(trial_data_provider.__length__()))
        controls = [
            self.q_number,
            self.add_inst1,
            self.play_inst,
            self.playb,
            self.audio,
            self.add_inst2,
            self.inst1,
            self.opinion1,
            self.inst2,
            self.opinion2,
            #self.reminder,
            self.nextb
        ]

        #time.sleep(1)
        super(TestViewBase, self).__init__("/trialview", controls=controls)
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

    def state_changed(self, e):
        super().state_changed(e)
        if e.data == 'completed':
            self.add_inst2.color=ft.colors.RED
            #self.add_inst1.color=ft.colors.BLACK
            self.add_inst2.update()
            #self.add_inst1.update()
            global jst_standard
            self.start_time = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S')
        elif e.data == 'playing':
            self.playb.disabled=True
            self.playb.update()

    def clicked(self, e):
        global trial_data_provider, eval_dict
        eval_dict['eval'].append('trial')
        eval_dict['key'].append(self.key)
        eval_dict['value1'].append(self.value1)
        eval_dict['value2'].append(self.value2)
        eval_dict['start_time'].append(self.start_time)
        eval_dict['end_time1'].append(self.end_time1)
        eval_dict['end_time2'].append(self.end_time2)
        eval_dict['path'].append(trial_data_provider.csv)

        try:
            key, path = trial_data_provider.__next__()
            e.page.views.pop()
            e.page.views.append(TrialView(key, path))
            e.page.update()
        except StopIteration:
            e.page.go('/intermview')

def main(page: ft.Page):
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_csv', type=str, required=True)
    parser.add_argument('--trial_csv', type=str, required=True)
    parser.add_argument('--output_csv', type=str, default="output.csv")

    args=parser.parse_args()

    global test_data_provider, trial_data_provider
    test_data_provider = DataProvider(args.test_csv, random=True)
    trial_data_provider = DataProvider(args.trial_csv)
    #speaker_data_provider = DataProvider(args.speaker_csv)

    page.title="ディサーリア向け明瞭度/自然性聴取試験"

    pop_flag = False

    def route_change(e):
        nonlocal pop_flag

        if pop_flag:
            pop_flag=False
        else:
            if page.route == '/':
                page.views.clear()
                page.views.append(TopView())
            elif page.route == '/testview':
                key, path = test_data_provider.__next__()
                page.views.append(TestView(key, path)) 
            elif page.route == '/trialview':
                key, path = trial_data_provider.__next__()
                page.views.append(TrialView(key, path))
            elif page.route == '/intermview':
                page.views.append(IntermView())
            elif page.route == '/lastview':
                page.views.append(LastView(args.output_csv))

    def view_pop(e):               
        nonlocal pop_flag
        pop_flag = True
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    #page.window_full_screen = True
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.views.clear()
    page.go("/")

ft.app(target=main)
