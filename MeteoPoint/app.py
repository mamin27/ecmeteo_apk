import android
from android.graphics import Paint, PorterDuff
from android.view import ViewGroup
from android.content import ContentValues
from android.widget import Button, CheckBox, EditText, LinearLayout, RelativeLayout, ListView, TextView, LayoutParams
from android.database.sqlite import SQLiteDatabase


class OnClick(implements=android.view.View[OnClickListener]):
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def onClick(self, view: android.view.View) -> void:
        self.callback(*self.args, **self.kwargs)


def _create_layout_params():
    params = RelativeLayout.LayoutParams(RelativeLayout.LayoutParams.WRAP_CONTENT,
                                         RelativeLayout.LayoutParams.WRAP_CONTENT)
    params.addRule(RelativeLayout.ALIGN_PARENT_RIGHT)
    return params


class StrikeableTextView(extends=android.widget.TextView):
    @super({context: android.content.Context})
    def __init__(self, context, striked=False):
        self.striked = striked
        self._repaint_strike()

    def setStriked(self, striked):
        self.striked = bool(striked)
        self._repaint_strike()

    def _repaint_strike(self):
        if self.striked:
            flags = self.getPaintFlags() | Paint.STRIKE_THRU_TEXT_FLAG
            self.setTextColor(0xffaaaaaa)
        else:
            flags = self.getPaintFlags() & ~Paint.STRIKE_THRU_TEXT_FLAG
            self.setTextColor(0xff111111)
        self.setPaintFlags(flags)


class TodoItem:
    def __init__(self, value, context, layout=None, callback=None):
        self.callback = callback
        self.context = context
        self.value = value
        if layout:
            self.layout = layout
            self.checkbox = layout.getChildAt(0)
            self.text_view = layout.getChildAt(1)
        else:
            self.layout = LinearLayout(self.context)
            self.checkbox = CheckBox(self.context)
            self.checkbox.setOnClickListener(OnClick(self.update))
            self.layout.addView(self.checkbox)
            
            print(value)
            self.text_view = StrikeableTextView(self.context, striked=value['finished'])
            self.text_view.setTextSize(25)
            self.layout.addView(self.text_view)
            
            self.button_delete = Button(self.context)
            self.button_delete.setOnClickListener(OnClick(self.delete))
            self.button_delete.getBackground().setColorFilter(0xffff4444, PorterDuff.Mode.MULTIPLY)
            self.button_delete.setText('X')
            relative1 = RelativeLayout(self.context) # relative inside horizontal layout
            relative1.addView(self.button_delete, _create_layout_params())
            self.layout.addView(relative1)

        self.text_view.setText(value['title'])
        self.checkbox.setChecked(value['finished'])

    def update(self):
        self.value['finished'] = self.checkbox.isChecked()
        self.text_view.setStriked(self.value['finished'])
        self.callback('update', self.value)

    def delete(self):
        self.callback('delete', self.value)

    def getView(self):
        return self.layout


class ListAdapter(extends=android.widget.BaseAdapter):
    def __init__(self, context, values, listener=None):
        self.listener = listener
        self.context = context
        self.values = list(values)

    def getCount(self) -> int:
        return len(self.values)

    def getItem(self, position: int) -> java.lang.Object:
        return self.values[position]

    def getItemId(self, position: int) -> long:
        return self.values[position]['id']

    def getView(self, position: int,
                view: android.view.View,
                container: android.view.ViewGroup) -> android.view.View:
        value = self.getItem(position)
        todo = TodoItem(value, self.context, callback=self.listener, layout=None)
        return todo.getView()


class TodoDB(extends=android.database.sqlite.SQLiteOpenHelper):
    @super({
        context: android.content.Context,
        "org.pybee.elias.todoapp": java.lang.String,
        None: android.database.sqlite.SQLiteDatabase[CursorFactory],
        1: int
    })
    def __init__(self, context):
        pass

    def onCreate(self, db: android.database.sqlite.SQLiteDatabase) -> void:
        print('initiating TodoDB')
        db.execSQL(
            "CREATE TABLE todo ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "title TEXT NOT NULL,"
            "finished BOOLEAN NOT NULL CHECK (finished IN (0,1))"
            ")"
        )

    def onUpgrade(self, db: android.database.sqlite.SQLiteDatabase,
                  oldVersion: int, newVersion: int) -> void:
        print('will upgrade database from', oldVersion, ' to', newVersion)
        raise NotImplementedError

    def add_item(self, item, finished=False):
        values = ContentValues()
        values.put("title", item)
        values.put("finished", finished)
        db = self.getWritableDatabase()
        db.insertWithOnConflict("todo", None, values, SQLiteDatabase.CONFLICT_REPLACE)
        db.close()

    def fetch_items(self):
        result = []

        db = self.getReadableDatabase()
        cursor = db.rawQuery("SELECT * FROM todo", None)
        while cursor.moveToNext():
            item_id = int(cursor.getInt(cursor.getColumnIndex('id')))
            title = cursor.getString(cursor.getColumnIndex('title'))
            finished = cursor.getInt(cursor.getColumnIndex('finished'))
            result.append(dict(id=item_id, title=title, finished=bool(finished)))
        db.close()

        return result

    def update_item(self, value):
        db = self.getWritableDatabase()
        db.execSQL(
            "UPDATE todo SET finished=%d WHERE id=%d"%(int(value['finished']), value['id'])
        )
        db.close()

    def delete_item(self, value):
        db = self.getWritableDatabase()
        db.execSQL(
            "DELETE FROM todo WHERE id=%d"%(value['id'])
        )
        db.close()

class MainApp:
    def __init__(self):
        self._activity = android.PythonActivity.setListener(self)
        self.db = TodoDB(self._activity)

    def _populate_db(self):
        self.db.add_item("get ice cream", finished=True)
        self.db.add_item("call mom", finished=False)
        self.db.add_item("buy plane tickets", finished=False)
        self.db.add_item("reserve hotel", finished=False)

    def onCreate(self):
        print('Starting TodoApp')
        self.dbitems = self.db.fetch_items()

        if not self.dbitems:
            print('populating DB')
            self._populate_db()
            self.dbitems = self.db.fetch_items()

        print('dbitems', self.dbitems)

        hlayout = LinearLayout(self._activity)
        hlayout.setOrientation(LinearLayout.HORIZONTAL)

        self.entry_text = EditText(self._activity)
        self.entry_text.setHint('Enter a new item...')
        hlayout.addView(self.entry_text)

        button_create = Button(self._activity)
        button_create.setText('Add')
        button_create.setOnClickListener(OnClick(self.create_item))

        rlayout = RelativeLayout(self._activity)
        rlayout.addView(button_create, _create_layout_params())
        hlayout.addView(rlayout)

        vlayout = LinearLayout(self._activity)
        vlayout.setOrientation(LinearLayout.VERTICAL)
        vlayout.addView(hlayout)

        self.adapter = ListAdapter(self._activity, self.dbitems,
                                   listener=self._dispatch_event)
        self.listView = ListView(self._activity)
        self.listView.setAdapter(self.adapter)

        vlayout.addView(self.listView)

        self._activity.setContentView(vlayout)

    def _dispatch_event(self, event, value):
        if event == 'update':
            self.update_item(value)
        elif event == 'delete':
            self.delete_item(value)
        else:
            raise ValueError('oops: got unkwnown event %s from %s' % (event, value))

    def update_item(self, value):
        self.db.update_item(value)

    def create_item(self):
        new_item_text = str(self.entry_text.getText())
        self.db.add_item(new_item_text, finished=False)
        self.dbitems = self.db.fetch_items()
        self.adapter.values = list(self.dbitems)
        self.listView.setAdapter(self.adapter)

    def delete_item(self, value):
        self.db.delete_item(value)
        self.dbitems = self.db.fetch_items()
        self.adapter.values = list(self.dbitems)
        self.listView.setAdapter(self.adapter)

def main():
    MainApp()
    
