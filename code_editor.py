from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt5.QtGui import (
    QColor, QPainter,
    QSyntaxHighlighter, QTextCharFormat, QFont, QTextFormat
)
from PyQt5.QtCore    import QRect, Qt, QRegExp

# единый фон редактора
EDITOR_BG = QColor(0x44, 0x57, 0x66)  # #445766

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

    def sizeHint(self):
        return self.codeEditor.lineNumberAreaWidth(), 0

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class SQLHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        # ключевые слова — оранжевый
        kwFmt = QTextCharFormat()
        kwFmt.setForeground(QColor(255,165,0))
        kwFmt.setFontWeight(QFont.Bold)
        for word in [
            "SELECT","FROM","WHERE","INSERT","UPDATE","DELETE",
            "CREATE","DROP","ALTER","JOIN","INNER","LEFT","RIGHT",
            "FULL","ON","AND","OR","VALUES","INTO","ORDER","BY","GROUP"
        ]:
            pat = QRegExp(r"\b" + word + r"\b", Qt.CaseInsensitive)
            self.rules.append((pat, kwFmt))

        # строковые литералы — светло-зелёные
        strFmt = QTextCharFormat()
        strFmt.setForeground(QColor(206,145,120))
        self.rules.append((QRegExp(r"'[^']*'"), strFmt))

        # числа — светло-фиолетовый
        numFmt = QTextCharFormat()
        numFmt.setForeground(QColor(197,134,192))
        self.rules.append((QRegExp(r"\b[0-9]+\b"), numFmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            idx = pattern.indexIn(text)
            while idx >= 0:
                length = pattern.matchedLength()
                self.setFormat(idx, length, fmt)
                idx = pattern.indexIn(text, idx + length)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # шрифт по умолчанию (моноширинный)
        # используем стандартный моноширинный шрифт macOS
        # моноширинный шрифт для SQL-редактора
        self.setFont(QFont("Consolas", 12))

        # фон редактора
        pal = self.palette()
        pal.setColor(self.backgroundRole(), EDITOR_BG)
        pal.setColor(self.foregroundRole(), QColor(220,220,220))
        self.setPalette(pal)

        # подсветка SQL
        self.highlighter = SQLHighlighter(self.document())

        # нумерация строк
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)

        # подсветка активной строки
        self.highlightCurrentLine()

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        return 5 + self.fontMetrics().width('9') * digits

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(
                0, rect.y(), self.lineNumberArea.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)

        # рамка полосы номеров
        pen = painter.pen()
        pen.setColor(EDITOR_BG)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(event.rect())

        # рисуем номера строк на фоне редактора
        painter.setPen(QColor(160,160,160))
        block = self.firstVisibleBlock()
        blockNum = block.blockNumber()
        top = int(self.blockBoundingGeometry(block)
                  .translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        fm = self.fontMetrics()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                num = str(blockNum + 1)
                painter.drawText(
                    0, top, self.lineNumberArea.width() - 4,
                    fm.height(), Qt.AlignRight, num
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNum += 1

    def highlightCurrentLine(self):
        extras = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            # заливка активной строки темно-синим
            sel.format.setBackground(QColor(58, 64, 74))
            sel.format.setProperty(QTextFormat.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            extras.append(sel)
        self.setExtraSelections(extras)
