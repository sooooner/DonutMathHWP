import re
import os
import uuid
import json
import win32com.client as win32

from .path import tmp_dir, pdf_folder, dataset_dir
from .utils import get_basename

delect_items = [(0, 3), (1, 4), (2, 90), (3, 16), (4, 26), (5, 25), (6, 20), (7, 31), (8, 32), (9, 21), (10, 43), (11, 44), (12, 45), (13, 46), (14, 93), (15, 61), (16, 92), (17, 22), (18, 56), (19, 58), (20, 15), (21, 59)]

def create_uuid_key(uuid_to_eqn):
    is_in = True
    is_digit = True
    while is_in or is_digit:
        uid = uuid.uuid4().hex[:4]
        is_digit = uid.isdigit()
        is_in = uid in uuid_to_eqn.keys()
    return uid

def replace_repeated_with_target(input_string, char, target=' '):
    pattern = f'({re.escape(char)}){{1,}}'
    replaced_string = re.sub(pattern, target, input_string)
    return replaced_string

class Hwp():
    def __init__(self):
        self.hwp = win32.gencache.EnsureDispatch("hwpframe.hwpobject")

    def run_hwp(self, path=None, visible=True):
        self.hwp.XHwpWindows.Item(0).Visible = visible
        self.hwp.RegisterModule("FilePathCheckDLL", "AutomationModule")
        if path:
            self.hwp.Open(path)

    def save_as_pdf(self, pdf_file_path):
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)

        self.hwp.HAction.GetDefault("FileSaveAsPdf", self.hwp.HParameterSet.HFileOpenSave.HSet)
        self.hwp.HParameterSet.HFileOpenSave.filename = pdf_file_path
        self.hwp.HParameterSet.HFileOpenSave.Format = "PDF"
        self.hwp.HParameterSet.HFileOpenSave.Attributes = 16384
        self.hwp.HAction.Execute("FileSaveAsPdf", self.hwp.HParameterSet.HFileOpenSave.HSet)

    def save_as_html(self, html_file_path):
        self.hwp.HAction.GetDefault("FileSaveAs_S", self.hwp.HParameterSet.HFileOpenSave.HSet)
        self.hwp.HParameterSet.HFileOpenSave.filename = html_file_path
        self.hwp.HParameterSet.HFileOpenSave.Format = "HTML+"
        self.hwp.HAction.Execute("FileSaveAs_S", self.hwp.HParameterSet.HFileOpenSave.HSet)
        return self.hwp

    def extract_eqn(self):
        Act = self.hwp.CreateAction("EquationModify")
        Set = Act.CreateSet()
        Pset = Set.CreateItemSet("EqEdit", "EqEdit")
        Act.GetDefault(Pset)
        return Pset.Item("String")

    def remove_head_type(self):
        self.hwp.HAction.Run("SelectAll")
        self.hwp.HAction.GetDefault("ParagraphShape", self.hwp.HParameterSet.HParaShape.HSet)
        self.hwp.HParameterSet.HParaShape.HSet.SetItem("HeadingType", None)
        self.hwp.HAction.Execute("ParagraphShape", self.hwp.HParameterSet.HParaShape.HSet)
        self.hwp.HAction.Run("MoveRight")

    def set_charshape(self):
        self.hwp.HAction.GetDefault("CharShape", self.hwp.HParameterSet.HCharShape.HSet)
        self.hwp.HParameterSet.HCharShape.Height = 1
        self.hwp.HAction.Execute("CharShape", self.hwp.HParameterSet.HCharShape.HSet)
        
    def insert_uid(self, uid):
        self.hwp.HAction.Run("Cancel")
        self.set_charshape()
        self.hwp.HAction.GetDefault("InsertText", self.hwp.HParameterSet.HInsertText.HSet)
        self.hwp.HParameterSet.HInsertText.Text = uid
        self.hwp.HAction.Execute("InsertText", self.hwp.HParameterSet.HInsertText.HSet)
        
    def insert_text(self, text):
        self.hwp.HParameterSet.HInsertText.Text = text
        self.hwp.HAction.Execute("InsertText", self.hwp.HParameterSet.HInsertText.HSet)

    def page_set_up(self):
        self.hwp.HAction.GetDefault("PageSetup", self.hwp.HParameterSet.HSecDef.HSet)
        self.hwp.HParameterSet.HSecDef.PageDef.PaperWidth = self.hwp.MiliToHwpUnit(257.0)
        self.hwp.HParameterSet.HSecDef.PageDef.PaperHeight = self.hwp.MiliToHwpUnit(364.0)
        self.hwp.HParameterSet.HSecDef.PageDef.LeftMargin = self.hwp.MiliToHwpUnit(18.0)
        self.hwp.HParameterSet.HSecDef.PageDef.RightMargin = self.hwp.MiliToHwpUnit(18.0)
        self.hwp.HParameterSet.HSecDef.PageDef.TopMargin = self.hwp.MiliToHwpUnit(10.0)
        self.hwp.HParameterSet.HSecDef.PageDef.BottomMargin = self.hwp.MiliToHwpUnit(10.0)
        self.hwp.HParameterSet.HSecDef.PageDef.HeaderLen = self.hwp.MiliToHwpUnit(25.0)
        self.hwp.HParameterSet.HSecDef.PageDef.FooterLen = self.hwp.MiliToHwpUnit(8.0)
        self.hwp.HParameterSet.HSecDef.HSet.SetItem("ApplyClass", 24)
        self.hwp.HParameterSet.HSecDef.HSet.SetItem("ApplyTo", 3)
        self.hwp.HAction.Execute("PageSetup", self.hwp.HParameterSet.HSecDef.HSet)

    def convet_tap_pt(self, pt=200.0):
        self.hwp.HAction.GetDefault("ModifySection", self.hwp.HParameterSet.HSecDef.HSet)
        self.hwp.HParameterSet.HSecDef.TabStop = self.hwp.PointToHwpUnit(pt)
        self.hwp.HParameterSet.HSecDef.HSet.SetItem("ApplyClass", 24)
        self.hwp.HParameterSet.HSecDef.HSet.SetItem("ApplyTo", 3)
        self.hwp.HAction.Execute("ModifySection", self.hwp.HParameterSet.HSecDef.HSet)

    def convert_multi_column(self):
        self.hwp.HAction.GetDefault("MultiColumn", self.hwp.HParameterSet.HColDef.HSet)
        self.hwp.HParameterSet.HColDef.Count = 2
        self.hwp.HParameterSet.HColDef.SameGap =  self.hwp.MiliToHwpUnit(8.0)
        self.hwp.HParameterSet.HColDef.LineType = self.hwp.HwpLineType("Solid")
        self.hwp.HParameterSet.HColDef.LineWidth = self.hwp.HwpLineWidth("0.12mm")
        self.hwp.HParameterSet.HColDef.HSet.SetItem("ApplyClass", 832)
        self.hwp.HParameterSet.HColDef.HSet.SetItem("ApplyTo", 6)
        self.hwp.HAction.Execute("MultiColumn", self.hwp.HParameterSet.HColDef.HSet)
        
    def insert_equation(self, equation):
        self.hwp.HAction.GetDefault("EquationCreate", self.hwp.HParameterSet.HEqEdit.HSet)
        self.hwp.HParameterSet.HEqEdit.string = equation
        self.hwp.HParameterSet.HEqEdit.EqFontName = "HancomEQN"
        self.hwp.HAction.Execute("EquationCreate", self.hwp.HParameterSet.HEqEdit.HSet)

        self.hwp.FindCtrl()
        self.hwp.HAction.GetDefault("EquationPropertyDialog", self.hwp.HParameterSet.HShapeObject.HSet)
        self.hwp.HParameterSet.HShapeObject.HSet.SetItem("ShapeType", 1)
        self.hwp.HParameterSet.HShapeObject.Version = "Equation Version 60"
        self.hwp.HParameterSet.HShapeObject.EqFontName = "HancomEQN"
        self.hwp.HParameterSet.HShapeObject.HSet.SetItem("ApplyTo", 1)
        self.hwp.HParameterSet.HShapeObject.HSet.SetItem("TreatAsChar", 1)
        self.hwp.HAction.Execute("EquationPropertyDialog", self.hwp.HParameterSet.HShapeObject.HSet)
        self.hwp.Run("Cancel")
        self.hwp.Run("MoveRight")

    def modify_eqn(self, string, uid):
        self.hwp.HAction.GetDefault("EquationModify", self.hwp.HParameterSet.HEqEdit.HSet)
        self.hwp.HParameterSet.HEqEdit.string = string + uid
        self.hwp.HAction.Execute("EquationModify", self.hwp.HParameterSet.HEqEdit.HSet)

    def delect_formatting(self, delect_items):
        self.hwp.HAction.GetDefault("DeleteCtrls", self.hwp.HParameterSet.HDeleteCtrls.HSet)
        self.hwp.HParameterSet.HDeleteCtrls.CreateItemArray("DeleteCtrlType", len(delect_items))
        for k, v in delect_items:
            self.hwp.HParameterSet.HDeleteCtrls.DeleteCtrlType.SetItem(k, v)
        self.hwp.HAction.Execute("DeleteCtrls", self.hwp.HParameterSet.HDeleteCtrls.HSet)

    def save_uuid_to_eqn(self, file_name, uuid_to_eqn):
        if not os.path.exists(dataset_dir):
            os.makedirs(dataset_dir)

        row = {
            'file_name': file_name,
            'uuid_to_eqn': uuid_to_eqn
        }

        file_path = os.path.join(dataset_dir, 'uuid_to_eqn.jsonl')
        file_mode = 'a' if os.path.exists(file_path) else 'w'
        with open(file_path, file_mode, encoding='utf-8') as file:
            json_string = json.dumps(row, ensure_ascii=False)
            file.write(json_string + '\n')

    def extract_uuid_to_eqn(self):
        ctrl = self.hwp.HeadCtrl 
        
        uuid_to_eqn = {}    
        while ctrl != None: 
            nextctrl = ctrl.Next 
            if ctrl.CtrlID == "eqed":  
                position = ctrl.GetAnchorPos(0) 
                position = position.Item("List"), position.Item("Para"), position.Item("Pos")
                self.hwp.SetPos(*position)  
                self.hwp.FindCtrl() 

                uid = create_uuid_key(uuid_to_eqn)
                eqn_string = self.extract_eqn()  
                self.insert_uid(uid)
                if eqn_string is not None:
                    eqn_string = replace_repeated_with_target(eqn_string, '`', ' ')
                    eqn_string = replace_repeated_with_target(eqn_string, '~', ' ')
                    eqn_string = replace_repeated_with_target(eqn_string, ' ', ' ')
                    uuid_to_eqn[uid] = eqn_string.replace('\r\n', '').strip()
                else:
                    continue

            ctrl = nextctrl  
        self.hwp.Run("Cancel")
        return uuid_to_eqn

    def extract_html(self, hwp_path, quit=True, visible=False, save=True):
        basename = get_basename(hwp_path)
        html_file_path = os.path.join(tmp_dir, basename) + '.html'
        pdf_file_path = os.path.join(pdf_folder, basename) + '.pdf'
        
        self.run_hwp(hwp_path, visible=visible)
        self.delect_formatting(delect_items)

        self.remove_head_type()
        pdf_file_path_ = os.path.join(pdf_folder, basename) + '_.pdf'
        self.save_as_pdf(pdf_file_path_)
        self.hwp.HAction.Run("Undo")

        self.save_as_pdf(pdf_file_path)
        uuid_to_eqn = self.extract_uuid_to_eqn()
        self.save_as_html(html_file_path)
        if save:
            self.save_uuid_to_eqn(basename, uuid_to_eqn)

        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        if quit:
            self.hwp.Clear(1)
            self.hwp.Quit()

        return html_content, uuid_to_eqn
    

