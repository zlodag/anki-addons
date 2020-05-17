from aqt import gui_hooks, mw, addcards, dialogs


def add_related_note(related_note_id, model_id, deck_id, fields_to_copy, copy_tags, browser):
    browser.col.decks.select(deck_id)
    current_deck = browser.col.decks.current()
    current_deck['mid'] = model_id
    browser.col.decks.save(current_deck)
    browser.col.models.setCurrent(browser.col.models.get(model_id))
    note_to_copy = browser.col.getNote(related_note_id)
    add_cards: addcards.AddCards = dialogs.open('AddCards', mw)
    new_note = add_cards.editor.note
    if copy_tags:
        new_note.tags = note_to_copy.tags
    for field in fields_to_copy:
        new_note[field] = note_to_copy[field]
    add_cards.setAndFocusNote(new_note)


def create_add_related_note_listener(related_note_id, model_id, deck_id, fields_to_copy, copy_tags, browser):
    return lambda: add_related_note(related_note_id, model_id, deck_id, fields_to_copy, copy_tags, browser)


def add_context_menu_items(browser, menu):
    note_ids = browser.selectedNotes()
    if len(note_ids) == 1:
        note = browser.col.getNote(note_ids[0])
        config = mw.addonManager.getConfig(__name__)
        menu.addSeparator()
        new_menu = menu.addMenu('Add related note')
        for related_note in config['related_notes']:
            field_set = set(related_note['fields_to_copy'])
            if field_set <= set(note.keys()):
                sub_menu = new_menu.addMenu(related_note['label'])
                for note_type in browser.col.models.all():
                    if field_set <= set(browser.col.models.fieldNames(note_type)):
                        action = sub_menu.addAction(note_type['name'])
                        action.triggered.connect(create_add_related_note_listener(
                            note.id,
                            note_type['id'],
                            note.model()['did'],
                            field_set,
                            related_note['copy_tags'],
                            browser
                        ))
                if sub_menu.isEmpty():
                    sub_menu.setDisabled(True)
        if new_menu.isEmpty():
            new_menu.setDisabled(True)


gui_hooks.browser_will_show_context_menu.append(add_context_menu_items)
