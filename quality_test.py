import flet as ft
import pandas as pd
import argparse
import time, datetime

#message0=['1: よくわかる', '2: ときどきわからない語がある', 
#          '3: 聞き手が話題を知っていればわかる', '4: ときどきわかる語がある', 
#          '5: 全くの了解不能']
#message1=['1: 全くの自然である（不自然な要素がない）', '2: やや不自然な要素がある', '3: 明らかに不自然である', '4: 顕著に不自然である', '5: 全く不自然である（自然な要素がない）']
#message2=['-2: 速い', '-1: やや速い', '0: 自然な速さである', '1: ややゆっくりしている', '2: ゆっくりしている',]
paths = ['/Users/akio/Documents/GitHub/ListeningTest/jnas_norm/NF009061.wav', '/Users/akio/Documents/GitHub/ListeningTest/jnas_norm/NM031061.wav', '/Users/akio/Documents/GitHub/ListeningTest/jnas_norm/NM040095.wav']
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
eval_dict = {'eval':[], 'key': [], 'intelligiblity': [], 'naturalness': [], 'cb1': [], 'cb2': [], 'cb3': [], 'cb4': [], 'start_time': [], 'end_time': [], 'path':[]}

class CBComponent(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.cb1 = ft.Checkbox(label='発音', value=False, disabled=True)
        self.cb2 = ft.Checkbox(label='速さ', value=False, disabled=True)
        self.cb3 = ft.Checkbox(label='単語のアクセント', value=False, disabled=True)
        self.cb4 = ft.Checkbox(label='全体の抑揚', value=False, disabled=True)

    def get_values(self):
        return self.cb1.value, self.cb2.value, self.cb3.value, self.cb4.value

    def enabled(self, enable):
        self.cb1.disabled=not enable
        self.cb1.update()
        self.cb2.disabled=not enable
        self.cb2.update()
        self.cb3.disabled=not enable
        self.cb3.update()
        self.cb4.disabled=not enable
        self.cb4.update()

    def build(self):
        title = ft.Text(
            spans=[
                ft.TextSpan('不自然に感じた要素があれば以下から選んでください（複数選択可）',
                            ft.TextStyle(size=16,))
            ]
        )
        
        return ft.Container(
            ft.Column([
                title,
                self.cb1, self.cb2, self.cb3, self.cb4
            ])
        )
    
class SliderComponent(ft.UserControl):

    def __init__(self, title, min=1.0, max=5.0, value=3.0, divisions=8):
        super().__init__()
        self.title = ft.Text(
            spans=[
                ft.TextSpan(title,
                            ft.TextStyle(size=16, weight=ft.FontWeight.BOLD))
            ]
        )
        
        self.divisions=divisions
        self.min=min
        self.max=max
        self.value=value

        self.slider=ft.Slider(
                    min=self.min,
                    max=self.max,
                    value=self.value,
                    adaptive=False,
                    divisions=self.divisions,
                    active_color=ft.colors.BLUE,
                    thumb_color=ft.colors.BLUE,
                    on_change_start=self.handle_change_start,
                    on_change_end=self.handle_change_end,
                    on_change = self.handle_change,
                    round=1,
                    label='{value}',
                    disabled=True
                )
    
    def build(self):
        self.slider_selected_value = self.value
        self.slider_status = ft.Text(self.slider_selected_value)

        return ft.Container(
            ft.Column([
                self.title,
                self.slider,
                self.slider_status
            ])
        )

    def handle_change_start(self, e):
        try:
            self.slider_status.value = e.control.value
            self.slider_selected_value = e.control.value
            self.slider_status.update()
            self.value = e.control.value
        except:
            pass
        #print(self.slider_selected_value)

    def handle_change_end(self, e):
        self.slider_status.value = e.control.value
        self.slider_selected_value = e.control.value
        self.slider_status.update()
        self.value = e.control.value
        #print(self.slider_selected_value)

    def handle_change(self, e):
        self.slider_status.value = e.control.value
        self.slider_selected_value = e.control.value
        self.slider_status.update()
        self.value = e.control.value        
        #print(self.slider_selected_value)

    def enabled(self, enable):
        self.slider.disabled=not enable
        self.slider.update()

    def get_value(self):
        return self.value

class VolumeAdjustView(ft.View):
    def prepare(self, path):
        audio = ft.Audio(src=path, volume=1, balance=0, autoplay=False)
        #controls.append(audio1)
        #controls.append(ft.Text('「再生」をクリックして音声を聞き取ってください。'))
        playb = ft.ElevatedButton(content=ft.Text("再生"), 
                                  on_click=lambda _: audio.play(), 
                                  disabled=False)
        playb.padding = ft.padding.only(top=100, bottom=100)
        #controls.append(playb1)
        return audio, playb
    def __init__(self, paths):
        controls = []
        controls.append(ft.Text(spans=[
            ft.TextSpan('ヘッドホンのボリュームを調整します')
        ]))

        audio1, playb1 = self.prepare(paths[0])
        audio2, playb2 = self.prepare(paths[1])
        audio3, playb3 = self.prepare(paths[2])

        controls.append(audio1)
        controls.append(ft.Text('サンプル①の再生'))
        controls.append(playb1)
        controls.append(audio2)
        controls.append(ft.Text('サンプル②の再生'))
        controls.append(playb2)
        controls.append(audio3)
        controls.append(ft.Text('サンプル③の再生'))
        controls.append(playb3)

        controls.append(ft.Text(' '))
        controls.append(ft.Text('調整したら「次へ」をクリックします。'))

        nextb = ft.ElevatedButton(content=ft.Text('次へ'), on_click=self.clicked)
        nextb.padding = ft.padding.only(top=200, bottom=200)
            
        controls.append(nextb)

        super().__init__("/volumeadjustview", controls=controls)
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER


    def clicked(self, e):
        e.page.go("/topview")

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
                        '実験では、さまざまな個人の音声がスピーカーから流れます。　　　　　　　　　',
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
                        'あります。　　　　　　　　　　　　　　　　　　　　　',
                    )
                ]
            ),
            ft.Text("　"),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '聞き取った音声について，明瞭性，自然さの観点から評価してください',
                    ),
                ]
            ),
            ft.Text("　"),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '明瞭性：音声の内容について「1:全くの了解不能」から「5:よくわかる」までの間で評価）　　　　　　　　',
                        ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ]
            ),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        '自然さ：聞き取った音声について「1:全く不自然である」から「5:全く自然である」までの間で評価　　　　',
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

class ViewBase(ft.View):
    def __init__(self, key, path):
        self.play_inst = ft.Text('「再生」をクリックして音声を聞き取ってください。')
        self.audio = ft.Audio(src=path, volume=1, balance=0, 
                         on_state_changed=self.state_changed,
                         on_loaded=self.activate_play_button,
                         autoplay=False)
        self.playb = ft.ElevatedButton(content=ft.Text("再生"), 
                                       on_click=lambda _: self.audio.play(), 
                                       disabled=True)
        self.playb.padding = ft.padding.only(top=50, bottom=100)        

        self.component1 = SliderComponent('明瞭度　選択の目安「1:全くの了解不能」「2:ところどころわかる語がある」「3:聞き手が話題を知っていればわかる（半分くらいわかる）」「4:ところどころわからない語がある」「5:よくわかる」', min=1, max=5, divisions=8)
        self.component2 = SliderComponent('自然さ　選択の目安「1:全く不自然である（自然な要素がない）」「2:顕著に不自然である」「3:明らかに不自然である」「4:やや不自然である」「5:全く自然である（不自然な要素がない）」　　　' , min=1, max=5, divisions=8)
        self.component3 = CBComponent()

        self.nextb = ft.ElevatedButton(content=ft.Text('次へ'), 
                                       on_click=self.clicked,
                                       disabled=True)
        self.nextb.padding = ft.padding.only(top=100)
        self.nextm = ft.Text('評価が終わったら「次へ」をクリックして進みます。', color=ft.colors.WHITE)

        self.key = key
        self.path = path
        self.start_time = None
        self.end_time = None

    
    def state_changed(self, e):
        if e.data == 'completed':
            self.playb.disabled=True
            self.playb.update()
            self.nextb.disabled=False
            self.nextb.update()
            self.component1.enabled(True)
            self.component2.enabled(True)
            self.component3.enabled(True)
        elif e.data == 'playing':
            self.playb.disabled=True
            self.playb.update()
            self.nextb.disabled=True
            self.nextb.update()

    def clicked(self, e):
        raise NotImplementedError()

    #def value_changed(self, e):
    #    raise NotImplementedError()

    def activate_play_button(self, e):
        self.playb.disabled=False
        self.playb.update()

class TestView(ViewBase):
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
            self.component1,
            self.component2,
            self.component3,
            self.nextm,
            self.nextb
        ]

        super(ViewBase, self).__init__("/testview", controls=controls)
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

    def state_changed(self, e):
        super().state_changed(e)
        if e.data == 'completed':
            global jst_standard
            self.start_time = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
        elif e.data == 'playing':
            self.playb.disabled=True
            self.playb.update()

    def clicked(self, e):
        global jst_standard 
        self.end_time = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S')
        global test_data_provider, eval_dict
        eval_dict['eval'].append('test')
        eval_dict['key'].append(self.key)
        eval_dict['intelligiblity'].append(self.component1.get_value())
        eval_dict['naturalness'].append(self.component2.get_value())

        eval_dict['start_time'].append(self.start_time)
        eval_dict['end_time'].append(self.end_time)
        eval_dict['path'].append(test_data_provider.csv)

        value1, value2, value3, value4 = self.component3.get_values()
        eval_dict['cb1'].append(value1)
        eval_dict['cb2'].append(value2)
        eval_dict['cb3'].append(value3)
        eval_dict['cb4'].append(value4)

        try:
            key, path = test_data_provider.__next__()
            e.page.views.pop()
            e.page.views.append(TestView(key, path))
            e.page.update()
        except StopIteration:
            e.page.go('/lastview')

    #def value_changed(self, e):
    #    self.nextm.color=ft.colors.BLACK
    #    self.nextm.update()
    #    global jst_standard
    #    self.end_time = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
    
class TrialView(ViewBase):
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

        controls = [
            self.q_number,
            self.add_inst1,
            self.play_inst,
            self.playb,
            self.audio,
            self.add_inst2,
            self.component1,
            self.component2,
            self.component3,
            self.nextb
        ]

        super(ViewBase, self).__init__("/trialview", controls=controls)
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

    def state_changed(self, e):
        super().state_changed(e)
        if e.data == 'completed':
            self.add_inst2.color=ft.colors.RED
            self.add_inst2.update()
            global jst_standard
            self.start_time = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S')
        elif e.data == 'playing':
            self.playb.disabled=True
            self.playb.update()

    def clicked(self, e):
        global jst_standard 
        self.end_time = datetime.datetime.now(jst_standard).strftime('%Y/%m/%d %H:%M:%S')

        global trial_data_provider, eval_dict
        eval_dict['eval'].append('trial')
        eval_dict['key'].append(self.key)
        eval_dict['start_time'].append(self.start_time)
        eval_dict['end_time'].append(self.end_time)
        eval_dict['path'].append(trial_data_provider.csv)
        eval_dict['intelligiblity'].append(self.component1.get_value())
        eval_dict['naturalness'].append(self.component2.get_value())
        value1, value2, value3, value4 = self.component3.get_values()
        print(value1)
        eval_dict['cb1'].append(value1)
        eval_dict['cb2'].append(value2)
        eval_dict['cb3'].append(value3)
        eval_dict['cb4'].append(value4)
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
    parser.add_argument('--output_csv', type=str, default="deaf_output.csv")

    args=parser.parse_args()

    global test_data_provider, trial_data_provider
    test_data_provider = DataProvider(args.test_csv, random=True)
    trial_data_provider = DataProvider(args.trial_csv, random=True)

    page.title="Speech Quality Test"

    pop_flag = False

    def route_change(e):
        nonlocal pop_flag

        if pop_flag:
            pop_flag=False
        else:
            if page.route == '/':
                page.views.clear()
                page.views.append(VolumeAdjustView(paths))
            elif page.route == '/topview':
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
            elif page.route == '/volumeadjustview':
                page.views.append(VolumeAdjustView(paths))

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
