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
eval_dict = {'eval':[], 'key': [], 'value': [], 'start_time': [], 'end_time': [], 'path': []}

class TopView(ft.View):
    def __init__(self):
        global test_data_provider
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
                        '実験参加者のあなたは、スピーカーから流れる音声を聞き取ります。　　',
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
                        'あります。　　　　　　　　　　　　　　　　　　　　　　　　',
                    )
                ]
            ),
            ft.Text("　"),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '聞き取りに要した労力にあわせて、次の',
                    ),
                    ft.TextSpan(
                        '５つ',
                        ft.TextStyle(size=14, weight=ft.FontWeight.BOLD)
                    ),
                    ft.TextSpan(
                        'の選択肢からひとつを選んで答えてください。',
                    )
                ]
            ),
            ft.Text("　"),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '「完全にリラックスして聴取できる」　　　　',
                        ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ]
            ),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '「注意を払う必要はあるが特別な努力は不要」',
                        ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ]
            ),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '「ある程度の努力が必要」　　　　　　　　　',
                        ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ]
            ),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '「かなりの努力が必要」　　　　　　　　　　',
                        ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ]
            ),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '「どんな努力をしても意味は理解できない」　',
                        ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ]
            ),
            ft.Text('　'),
            ft.Text('準備ができたら「次へ」をクリックして進みます。'),
            ft.ElevatedButton(content=ft.Text('次へ'), on_click=self.clicked)
        ]
        super().__init__("/", controls=controls)
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

    def clicked(self, e):
        e.page.go("/testview")

class SpeakerView(ft.View):
    def __init__(self, key, path):

        self.audio = ft.Audio(src=path, volume=1, balance=0, 
                         on_loaded=self.activate_play_button,
                         on_state_changed=self.state_changed,
                         autoplay=False)
        
        self.playb = ft.ElevatedButton(content=ft.Text("再生"), 
                                       on_click=lambda _: self.audio.play(), 
                                       disabled=False)
        self.playb.padding = ft.padding.only(top=50, bottom=200)

        self.nextb = ft.ElevatedButton(content=ft.Text('次へ'), 
                                       on_click=self.clicked,
                                       disabled=True)
        #self.nextb.padding = ft.padding.only(top=100)
        
        global spekaer_data_provider
        controls = [
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '聞き取りの対象となる話者は'
                    ),
                    ft.TextSpan(
                        str(speaker_data_provider.__length__()),
                        ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    ),
                    ft.TextSpan(
                        '人になります。'
                    )
                ]
            ),
            ft.Text('　'),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '下にある「再生」をクリックして'
                    ),
                    ft.TextSpan(
                        str(speaker_data_provider.counter),
                        ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    ),
                    ft.TextSpan(
                        '人目の話者の音声を聞き取って、声の特徴を覚えてください。'
                    ),
                ]
            ),
            ft.Text('覚えるまで再生は繰り返しても構いません。'),
            ft.Text("　"),
            self.playb,
            self.audio,
            ft.Text("　"),
            ft.Text("　"),
            ft.Text('覚えたら次へ進みます。'),
            self.nextb
        ]

        super(SpeakerView, self).__init__("/speakerview", controls=controls)
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

    def clicked(self, e):
        global speaker_data_provider
        try:
            key, path = speaker_data_provider.__next__()
            e.page.views.pop()
            e.page.views.append(SpeakerView(key, path))
            e.page.update()
        except StopIteration:
            e.page.go('/intermview')

    def activate_play_button(self, e):
        self.playb.disabled=False
        self.playb.update()
    
    def state_changed(self, e):
        if e.data == 'completed':
            self.playb.disabled=False
            self.playb.update()
            self.nextb.disabled=False
            self.nextb.update()
        elif e.data == 'playing':
            self.playb.disabled=True
            self.playb.update()
            self.nextb.disabled=True
            self.nextb.update()

class IntermView(ft.View):
    def __init__(self):
        global speaker_data_provider
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
                        '音声は複数の人の声が混じりあって再生されますが、　　　　　　　　　　　　　　　'
                    )
                ]
            ),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        str(speaker_data_provider.__length__()),
                        ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                    ),
                    ft.TextSpan(
                        '人のうちの誰かひとり（対象者）の声が必ず入っています。　　　　　　　　　　　'
                    )
                ]
            ),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '対象者の声の聞き取りに関して、実験のはじめに説明した５段階で評価してください。'
                    )
                ]
            ),
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
        self.audio, self.opinion = self.setup(path)
        self.inst = ft.Text('対象者の音声の聞き取りに関して以下の5段階で評価してください。', 
                            color=ft.colors.WHITE)
        self.inst.padding=ft.padding.only(top=200)
        #self.opinion.padding = ft.padding.only(left=1024, bottom=50)
        self.opinion.padding = ft.padding.only(left=256, bottom=50)
        self.nextb = ft.ElevatedButton(content=ft.Text('次へ'), 
                                       on_click=self.clicked,
                                       disabled=True)
        self.nextb.padding = ft.padding.only(top=100)
        self.nextm = ft.Text('評価が終わったら「次へ」をクリックして進みます。', color=ft.colors.WHITE)

        self.key = key
        self.path = path
        self.value = None
        self.start_time = None
        self.end_time = None

    def setup(self, src):
        audio = ft.Audio(src=src, volume=1, balance=0, 
                         on_state_changed=self.state_changed,
                         on_loaded=self.activate_play_button,
                         autoplay=False)
        self.radio1 = ft.Radio(value="5", label="完全にリラックスして聴取できる", disabled=True )
        self.radio2 = ft.Radio(value="4", label="注意を払う必要はあるが特別な努力は不要", disabled=True)
        self.radio3 = ft.Radio(value="3", label="ある程度の努力が必要", disabled=True)
        self.radio4 = ft.Radio(value="2", label="かなりの努力が必要", disabled=True)
        self.radio5 = ft.Radio(value="1", label="どんな努力をしても意味は理解できない", disabled=True)
        opinion = ft.Container(content=ft.RadioGroup(content=ft.Column([
            self.radio1, self.radio2, self.radio3, self.radio4, self.radio5
        ]), on_change=self.value_changed))
        return audio, opinion
    
    def state_changed(self, e):
        if e.data == 'completed':
            self.radio1.disabled=False
            self.radio1.update()
            self.radio2.disabled=False
            self.radio2.update()
            self.radio3.disabled=False
            self.radio3.update()
            self.radio4.disabled=False
            self.radio4.update()
            self.radio5.disabled=False
            self.radio5.update()

    def clicked(self, e):
        raise NotImplementedError()

    def value_changed(self, e):
        raise NotImplementedError()

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
            self.inst,
            self.opinion,
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
            self.inst.color=ft.colors.BLACK
            self.inst.update()
            global jst_standard
            self.start_time = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
        elif e.data == 'playing':
            self.playb.disabled=True
            self.playb.update()

    def clicked(self, e):
        global test_data_provider, eval_dict
        eval_dict['eval'].append('test')
        eval_dict['key'].append(self.key)
        eval_dict['value'].append(self.value)
        eval_dict['start_time'].append(self.start_time)
        eval_dict['end_time'].append(self.end_time)
        eval_dict['path'].append(test_data_provider.csv)

        try:
            key, path = test_data_provider.__next__()
            e.page.views.pop()
            e.page.views.append(TestView(key, path))
            e.page.update()
        except StopIteration:
            e.page.go('/lastview')

    def value_changed(self, e):
        self.value = e.data
        self.nextb.disabled=False
        self.nextb.update()
        self.nextm.color=ft.colors.BLACK
        self.nextm.update()
        global jst_standard
        self.end_time = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
    
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
            self.inst,
            self.opinion,
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
            self.inst.color=ft.colors.BLACK
            self.add_inst2.update()
            self.inst.update()
            global jst_standard
            self.start_time = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S')
        elif e.data == 'playing':
            self.playb.disabled=True
            self.playb.update()

    def clicked(self, e):
        global trial_data_provider, eval_dict
        eval_dict['eval'].append('trial')
        eval_dict['key'].append(self.key)
        eval_dict['value'].append(self.value)
        eval_dict['start_time'].append(self.start_time)
        eval_dict['end_time'].append(self.end_time)
        eval_dict['path'].append(trial_data_provider.csv)

        try:
            key, path = trial_data_provider.__next__()
            #print(key)
            e.page.views.pop()
            e.page.views.append(TrialView(key, path))
            e.page.update()
        except StopIteration:
            e.page.go('/intermview')

    def value_changed(self, e):
        self.value = e.data
        self.nextb.disabled=False
        self.nextb.update()
        global jst_standard 
        self.end_time = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S')

def main(page: ft.Page):
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_csv', type=str, required=True)
    #parser.add_argument('--speaker_csv', type=str, required=True)
    parser.add_argument('--output_csv', type=str, default="output.csv")

    args=parser.parse_args()

    global test_data_provider
    #, speaker_data_provider
    test_data_provider = DataProvider(args.test_csv, random=True)
    #trial_data_provider = DataProvider(args.trial_csv)
    #speaker_data_provider = DataProvider(args.speaker_csv)

    page.title="ITU-T 800 Listening Effort"

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
            elif page.route == '/speakerview':
                key, path = speaker_data_provider.__next__()
                page.views.append(SpeakerView(key, path))
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
