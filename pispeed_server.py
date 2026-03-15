const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  VerticalAlign, UnderlineType, LevelFormat
} = require('docx');
const fs = require('fs');

const BLUE = "2563EB";
const DARK = "1E293B";
const GRAY = "64748B";
const LIGHT_BG = "F1F5F9";
const CODE_BG = "1E293B";
const CODE_FG = "E2E8F0";
const GREEN = "16A34A";
const WARN = "D97706";

const bullet = (text, level = 0) => new Paragraph({
  numbering: { reference: "bullets", level },
  children: [new TextRun({ text, font: "Arial", size: 22, color: DARK })]
});

const numberedStep = (text, level = 0) => new Paragraph({
  numbering: { reference: "steps", level },
  children: [new TextRun({ text, font: "Arial", size: 22, color: DARK })]
});

const p = (text, opts = {}) => new Paragraph({
  spacing: { after: 160 },
  children: [new TextRun({ text, font: "Arial", size: 22, color: opts.color || DARK, bold: opts.bold || false, italics: opts.italic || false })]
});

const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 400, after: 200 },
  children: [new TextRun({ text, font: "Arial", size: 36, bold: true, color: BLUE })]
});

const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 300, after: 160 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "E2E8F0", space: 4 } },
  children: [new TextRun({ text, font: "Arial", size: 26, bold: true, color: DARK })]
});

const h3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  spacing: { before: 240, after: 120 },
  children: [new TextRun({ text, font: "Arial", size: 24, bold: true, color: BLUE })]
});

const codeBlock = (lines) => {
  return lines.map((line, i) => new Paragraph({
    spacing: { before: i === 0 ? 80 : 0, after: i === lines.length - 1 ? 80 : 0 },
    shading: { type: ShadingType.CLEAR, fill: CODE_BG },
    indent: { left: 360 },
    children: [new TextRun({
      text: line,
      font: "Courier New",
      size: 20,
      color: CODE_FG
    })]
  }));
};

const note = (text, type = "info") => {
  const colors = { info: "EFF6FF", warn: "FFFBEB", ok: "F0FDF4" };
  const borders = { info: "3B82F6", warn: "F59E0B", ok: "22C55E" };
  const icons = { info: "ℹ  ", warn: "⚠  ", ok: "✅  " };
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    shading: { type: ShadingType.CLEAR, fill: colors[type] },
    border: { left: { style: BorderStyle.THICK, size: 12, color: borders[type], space: 8 } },
    indent: { left: 360, right: 360 },
    children: [
      new TextRun({ text: icons[type], font: "Arial", size: 22 }),
      new TextRun({ text, font: "Arial", size: 22, color: DARK })
    ]
  });
};

const spacer = () => new Paragraph({ spacing: { after: 160 }, children: [new TextRun("")]});

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "steps",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL,
          text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET,
          text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } }, run: { font: "Arial" } }
        }]
      }
    ]
  },
  styles: {
    default: {
      document: { run: { font: "Arial", size: 22, color: DARK } }
    },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: BLUE },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 }
      },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: DARK },
        paragraph: { spacing: { before: 300, after: 160 }, outlineLevel: 1 }
      },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: BLUE },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 2 }
      },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [

      // ── Cover ──────────────────────────────────────────────
      new Paragraph({
        spacing: { before: 720, after: 240 },
        children: [new TextRun({ text: "📡  PiSpeed Monitor", font: "Arial", size: 52, bold: true, color: BLUE })]
      }),
      new Paragraph({
        spacing: { after: 80 },
        children: [new TextRun({ text: "Complete Installation & User Guide", font: "Arial", size: 30, color: GRAY })]
      }),
      new Paragraph({
        spacing: { after: 720 },
        children: [new TextRun({ text: "For Raspberry Pi OS  •  Pi-hole v6 Compatible  •  Linux Beginner Friendly", font: "Arial", size: 22, color: GRAY, italics: true })]
      }),

      note("This guide is written for complete Linux beginners. Every command is explained. Take it one step at a time — you've got this!", "ok"),

      spacer(),

      // ── What You Need ──────────────────────────────────────
      h1("Before You Start — What You Need"),

      p("Before installing PiSpeed Monitor, make sure you have the following:"),
      bullet("A Raspberry Pi running Raspberry Pi OS (any model — Pi 3, Pi 4, Pi Zero 2 W, etc.)"),
      bullet("Pi-hole already installed on that Pi (or just a bare Raspberry Pi OS — PiSpeed works either way)"),
      bullet("Your Pi connected to your home network via Wi-Fi or Ethernet cable"),
      bullet("A computer, tablet, or phone on the same network to access the web interface"),
      bullet("A keyboard and screen connected to the Pi (or SSH access if you know how)"),
      spacer(),

      note("You do NOT need to know Linux commands — this guide walks you through every single step.", "info"),

      spacer(),

      // ── How to Open Terminal ──────────────────────────────
      h1("Step 1 — Open the Terminal on Your Pi"),

      p("The 'Terminal' is like a command window — it's where you type instructions for your Pi."),
      spacer(),

      h3("Option A — You have a keyboard & monitor connected to your Pi"),
      ...codeBlock([
        "1. Look at your Pi's desktop",
        "2. Find the Terminal icon at the top of the screen (it looks like a black box with > prompt)",
        "3. Click it to open the Terminal",
      ]),
      spacer(),

      h3("Option B — You're connecting from another computer (SSH)"),
      p("SSH lets you control your Pi remotely from your laptop or desktop."),
      spacer(),

      p("On Windows — open PowerShell or Command Prompt and type:", { bold: true }),
      ...codeBlock(["ssh pi@<your-pi-ip-address>"]),
      p("Replace <your-pi-ip-address> with your Pi's IP (e.g. 192.168.1.50). If you're not sure, log into your router to find it."),
      spacer(),

      p("On Mac or Linux — open Terminal and type:", { bold: true }),
      ...codeBlock(["ssh pi@<your-pi-ip-address>"]),
      spacer(),

      p("The default password is: raspberry (unless you changed it during setup)", { italic: true }),
      spacer(),

      note("If you get a message about 'fingerprint' or 'authenticity', type yes and press Enter.", "info"),

      spacer(),

      // ── Step 2: Install Git ───────────────────────────────
      h1("Step 2 — Install Git (Download Tool)"),

      p("Git is a tool that downloads software. We need it to grab the PiSpeed installer files. Type the following commands one at a time, pressing Enter after each:"),
      spacer(),

      p("First, update your Pi's software list:", { bold: true }),
      ...codeBlock(["sudo apt update"]),
      spacer(),

      p("Then install git:", { bold: true }),
      ...codeBlock(["sudo apt install -y git"]),
      spacer(),

      note("When you see 'sudo' at the start of a command, it means 'run as administrator'. Your Pi might ask for your password — just type it (you won't see the letters as you type — that's normal!) and press Enter.", "info"),

      spacer(),

      // ── Step 3: Download PiSpeed ──────────────────────────
      h1("Step 3 — Download PiSpeed Monitor"),

      p("Now we'll download the PiSpeed Monitor files to your Pi. Type this command:"),
      spacer(),

      ...codeBlock(["git clone https://github.com/your-username/pispeed-monitor.git"]),
      spacer(),

      p("This creates a folder called pispeed-monitor on your Pi with all the files inside. Now move into that folder:"),
      ...codeBlock(["cd pispeed-monitor"]),
      spacer(),

      note("'cd' stands for 'change directory' — it's like double-clicking a folder to open it.", "info"),

      spacer(),

      // ── Step 4: Run Installer ─────────────────────────────
      h1("Step 4 — Run the Installer"),

      p("Now run the installer script. This will ask you a few questions about your internet plan:"),
      spacer(),

      ...codeBlock(["sudo bash install.sh"]),
      spacer(),

      h3("The installer will ask you these questions:"),
      spacer(),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "What port should the web UI run on?", font: "Arial", size: 22, bold: true, color: DARK })]
      }),
      p("Just press Enter to accept the default (8080). This is safe and won't conflict with Pi-hole."),
      spacer(),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "What download speed does your ISP plan include?", font: "Arial", size: 22, bold: true, color: DARK })]
      }),
      p("Type the speed your internet provider advertises. For example, if you pay for '100 Mbps broadband', type 100 and press Enter."),
      spacer(),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "What upload speed does your ISP plan include?", font: "Arial", size: 22, bold: true, color: DARK })]
      }),
      p("This is usually lower than download. If unsure, check your ISP's website or bill. A common value is 20."),
      spacer(),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "Alert threshold %", font: "Arial", size: 22, bold: true, color: DARK })]
      }),
      p("Press Enter for the default 80%. This means PiSpeed will flag any test where your speed dropped below 80% of what you're paying for."),
      spacer(),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "How often should automatic speedtests run? (minutes)", font: "Arial", size: 22, bold: true, color: DARK })]
      }),
      p("Press Enter for the default of 60 (every hour). You can always change this later in the web UI."),
      spacer(),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "Which speedtest backend?", font: "Arial", size: 22, bold: true, color: DARK })]
      }),
      p("Press Enter for option 1 (Auto-detect). The installer will install whichever tool works best."),
      spacer(),

      note("The installer may take 2–5 minutes while it downloads and sets up the speedtest tools. This is normal — just let it run.", "info"),

      spacer(),

      // ── Step 5: Find your Pi IP ───────────────────────────
      h1("Step 5 — Find Your Pi's IP Address"),

      p("When the installer finishes, it will show a message like:"),
      spacer(),

      ...codeBlock([
        "✅  PiSpeed Monitor installed successfully!",
        "",
        "Open your browser and go to:",
        "    http://192.168.1.50:8080",
      ]),
      spacer(),

      p("Note down that address. If you missed it, you can find your IP address by typing:"),
      ...codeBlock(["hostname -I"]),
      p("This will show a number like 192.168.1.50 — that's your Pi's address on your home network."),

      spacer(),

      // ── Step 6: Open the Web UI ───────────────────────────
      h1("Step 6 — Open PiSpeed Monitor in Your Browser"),

      p("On any device connected to your home network (laptop, phone, tablet):"),
      spacer(),

      numberedStep("Open a web browser (Chrome, Firefox, Safari, Edge — any will work)"),
      numberedStep("In the address bar at the top, type your Pi's address followed by :8080"),
      spacer(),

      ...codeBlock(["Example: http://192.168.1.50:8080"]),
      spacer(),

      numberedStep("Press Enter — the PiSpeed Monitor dashboard should appear!"),
      spacer(),

      note("It won't have any data yet — the first automatic test runs about 2 minutes after installation. You can also click the blue 'Run Speedtest Now' button to run one immediately.", "ok"),

      spacer(),

      // ── Using the Dashboard ───────────────────────────────
      h1("Step 7 — Using the Dashboard"),

      h3("Dashboard (Home Page)"),
      p("This is your main view. You'll see:"),
      bullet("4 stat cards at the top — your latest download speed, upload speed, ping, and total tests run"),
      bullet("A large graph showing your speeds over time with a reference line for your ISP's plan speed"),
      bullet("A smaller ping graph below"),
      bullet("A table of recent test results"),
      bullet("'Run Speedtest Now' button — click this any time you want an instant test"),
      spacer(),

      h3("History Page"),
      p("A full table of every speedtest ever run, with the ability to export as CSV or JSON. Use CSV to open in Excel or Google Sheets and create your own charts."),
      spacer(),

      h3("Violations Page"),
      p("This is your ISP accountability log. Every test that fell below your threshold — or any detected outage — appears here. You can screenshot this page or export the data to use as evidence when calling your ISP to complain about speeds."),
      spacer(),

      h3("Settings Page"),
      p("Change any configuration without touching the command line:"),
      bullet("Update your ISP plan speeds (e.g. if you upgrade your plan)"),
      bullet("Change the alert threshold percentage"),
      bullet("Adjust how often tests run"),
      bullet("Switch speedtest backends"),
      spacer(),

      note("After changing settings, click 'Save Settings'. The timer will automatically restart with your new interval.", "info"),

      spacer(),

      // ── Reading the Graph ─────────────────────────────────
      h1("Step 8 — Understanding the Speed Graph"),

      p("The main graph shows multiple lines:"),
      spacer(),

      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ shading: { fill: "2563EB" }, children: [new Paragraph({ children: [new TextRun({ text: "Line / Colour", font: "Arial", bold: true, color: "FFFFFF", size: 20 })] })] }),
              new TableCell({ shading: { fill: "2563EB" }, children: [new Paragraph({ children: [new TextRun({ text: "What it means", font: "Arial", bold: true, color: "FFFFFF", size: 20 })] })] }),
            ]
          }),
          new TableRow({ children: [
            new TableCell({ shading: { fill: "EFF6FF" }, children: [new Paragraph({ children: [new TextRun({ text: "Blue line", font: "Arial", size: 20, bold: true, color: "3B82F6" })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Your actual download speed at each test", font: "Arial", size: 20 })] })] }),
          ]}),
          new TableRow({ children: [
            new TableCell({ shading: { fill: "F0FDF4" }, children: [new Paragraph({ children: [new TextRun({ text: "Green line", font: "Arial", size: 20, bold: true, color: "22D3A5" })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Your actual upload speed at each test", font: "Arial", size: 20 })] })] }),
          ]}),
          new TableRow({ children: [
            new TableCell({ shading: { fill: "FFF7ED" }, children: [new Paragraph({ children: [new TextRun({ text: "Orange dashed line", font: "Arial", size: 20, bold: true, color: "FF6B35" })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Your ISP's advertised plan speed — what you're paying for", font: "Arial", size: 20 })] })] }),
          ]}),
          new TableRow({ children: [
            new TableCell({ shading: { fill: "FFFBEB" }, children: [new Paragraph({ children: [new TextRun({ text: "Yellow dashed line", font: "Arial", size: 20, bold: true, color: "F59E0B" })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Alert threshold — speeds below this are flagged", font: "Arial", size: 20 })] })] }),
          ]}),
          new TableRow({ children: [
            new TableCell({ shading: { fill: "FEF2F2" }, children: [new Paragraph({ children: [new TextRun({ text: "Red dots", font: "Arial", size: 20, bold: true, color: "EF4444" })] })] }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Individual tests that fell below your threshold — problem points!", font: "Arial", size: 20 })] })] }),
          ]}),
        ]
      }),

      spacer(),
      p("Hover over any dot on the graph to see the exact speed and time of that test."),
      p("Use the 24h / 7d / 30d / All buttons to change the time range shown."),

      spacer(),

      // ── Using Data Against ISP ────────────────────────────
      h1("Step 9 — Using PiSpeed to Challenge Your ISP"),

      p("This is one of the most powerful uses of PiSpeed Monitor:"),
      spacer(),

      numberedStep("Go to the Violations page — this shows every time your speed dropped below your paid threshold"),
      numberedStep("Note the dates, times, and speeds recorded"),
      numberedStep("Click 'Export CSV' on the History page to download a spreadsheet of all your data"),
      numberedStep("When you call or chat with your ISP, tell them: 'I have logged speed test data showing consistent drops below my contracted speed'"),
      numberedStep("Share the CSV file or screenshots of the Violations page as evidence"),
      numberedStep("Ask for a credit, speed boost, engineer visit, or contract renegotiation"),
      spacer(),

      note("ISPs are far more likely to take action when you have timestamped data logs. Anecdotal 'it seems slow sometimes' gets ignored — logged evidence does not.", "warn"),

      spacer(),

      // ── Useful Commands ───────────────────────────────────
      h1("Useful Commands Reference"),

      p("Open a terminal on your Pi and use these commands whenever you need them:"),
      spacer(),

      h3("Run a speedtest right now (from terminal)"),
      ...codeBlock(["sudo pispeed-run"]),
      spacer(),

      h3("Check if PiSpeed is running"),
      ...codeBlock(["sudo systemctl status pispeed"]),
      spacer(),

      h3("Restart PiSpeed (if something seems wrong)"),
      ...codeBlock(["sudo systemctl restart pispeed"]),
      spacer(),

      h3("View live logs"),
      ...codeBlock(["sudo journalctl -u pispeed -f"]),
      p("Press Ctrl+C to stop watching logs."),
      spacer(),

      h3("See when the next scheduled test will run"),
      ...codeBlock(["sudo systemctl list-timers pispeed-timer.timer"]),
      spacer(),

      h3("Uninstall PiSpeed Monitor"),
      ...codeBlock([
        "cd ~/pispeed-monitor",
        "sudo bash uninstall.sh"
      ]),
      spacer(),

      // ── Troubleshooting ───────────────────────────────────
      h1("Troubleshooting"),

      h3("'I can't open the web page in my browser'"),
      bullet("Make sure you're on the same Wi-Fi network as your Pi"),
      bullet("Double-check the IP address using: hostname -I (run this on your Pi)"),
      bullet("Check PiSpeed is running: sudo systemctl status pispeed"),
      bullet("Try restarting it: sudo systemctl restart pispeed"),
      spacer(),

      h3("'The speedtest fails or shows 0 Mbps'"),
      bullet("Check your Pi has internet access: ping -c 3 google.com"),
      bullet("Try running a test manually: sudo pispeed-run"),
      bullet("Check logs for errors: sudo journalctl -u pispeed-run -n 50"),
      spacer(),

      h3("'The graph has no data'"),
      bullet("Click the 'Run Speedtest Now' button to trigger a manual test"),
      bullet("Wait 2–3 minutes and refresh the page"),
      bullet("Automatic tests start running after about 2 minutes post-install"),
      spacer(),

      h3("'I forgot my Pi's IP address'"),
      ...codeBlock(["hostname -I"]),
      spacer(),

      note("If you get stuck, the most helpful command is: sudo journalctl -u pispeed -n 50 — it shows the last 50 lines of log which usually tells you exactly what's wrong.", "info"),

      spacer(),

      // ── Summary ───────────────────────────────────────────
      h1("Quick Start Summary"),

      new Paragraph({
        spacing: { after: 160 },
        children: [new TextRun({ text: "The 4 commands you need to install everything:", font: "Arial", size: 22, bold: true, color: DARK })]
      }),
      spacer(),

      ...codeBlock([
        "sudo apt update && sudo apt install -y git",
        "git clone https://github.com/your-username/pispeed-monitor.git",
        "cd pispeed-monitor",
        "sudo bash install.sh",
      ]),

      spacer(),
      p("Then open http://<your-pi-ip>:8080 in your browser. Done! ✅", { bold: true }),

      spacer(),
      new Paragraph({
        spacing: { before: 400 },
        children: [new TextRun({ text: "PiSpeed Monitor  •  MIT License  •  github.com/your-username/pispeed-monitor", font: "Arial", size: 18, color: GRAY, italics: true })]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/mnt/user-data/outputs/PiSpeed_Monitor_Installation_Guide.docx', buffer);
  console.log('Done!');
});
