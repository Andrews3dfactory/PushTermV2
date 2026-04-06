# 🖨️ PushTerm

**PushTerm** is a retro-style terminal tool that lets you auto-modify G-code for the Bambu Lab X1 Carbon printer. Its special feature? It inserts custom push-off logic into the G-code so the printer’s toolhead can physically eject a finished print from the build plate after a cooldown delay — all without needing extra hardware like a Raspberry Pi.

---

## 🙌 Shoutout

Special thanks to **[Small Pot](https://makerworld.com/en/models/1021588-small-pot?from=search#profileId-1003062)** (user_1400159957) for the awesome print design used during testing! 🎉

---

## 📂 Folder Structure

```
PushTerm/
├── launcher.py          # Opens the terminal UI in a separate window
├── terminal_ui.py       # Main terminal interface logic
├── gcode_modifier.py    # Inserts push-off logic into G-code
├── MyPrints/            # Where you put your original G-code files
│   └── Ploter.gcode     # (example file)
└── README.md            # This file
```

---

## 🧪 How to Use

1. **Download or clone** this project folder.
2. Put your G-code file (e.g., `Ploter.gcode`) inside the `MyPrints` folder.
3. Double-click or run this from the terminal:

   ```
   python launcher.py
   ```

4. When the terminal opens, follow the steps:
   - Type: `cd MyPrints`
   - Then: `begin`
   - Enter your file name: `Ploter.gcode`
   - Set the delay like `m5` for 5 minutes or `s30` for 30 seconds
   - Confirm how many copies to eject

5. The modified file will be saved in the same folder as:

   ```
   Ploter_modified.gcode
   ```

---

## ⚙️ What It Does

- Finds the end of your G-code file
- Adds a delay after the print finishes (based on your input)
- Inserts a G-code movement command to push the print off the bed using the toolhead
- Ensures safe travel height to avoid nozzle damage

---

## ✅ Requirements

- Python 3.x installed
- No extra dependencies — just basic Python and a terminal

---

## 🚨 Notes

- Always test modified G-code carefully.
- Use a safe push-off height to avoid nozzle damage.
- Works best on flat, hard-surface plates (like cool PEI or textured beds).
- Designed for Bambu Lab X1 Carbon but can be adapted.

---

## 🧠 Why This Exists

Because it’s fun to make your printer kick your prints off the bed like a boss.

---

## 📷 Screenshots or Demo

(You can add your YouTube video link or images here once ready.)

---

Created with 💚 by Andrew’s 3D Factory
📄 Licensed under the MIT License – see the LICENSE.md file for details.
