# %% A Gradio ChatInterface with persona controls and visible tool receipts
import gradio as gr

CSS = """
body, .gradio-container {background:#f5f4ef!important;color:#25332d;}
.gradio-container {width:100%!important;max-width:1100px!important;margin:0 auto!important;padding:20px 28px 14px!important;}
.gradio-container > .main {padding:0!important;}
.gradio-container main > .column {gap:12px;}
.club-header {display:flex;align-items:center;justify-content:space-between;gap:24px;padding:0 0 12px;}
.club-header h1 {font-family:Georgia,'Times New Roman',serif;font-size:32px;line-height:1.2;font-weight:400;letter-spacing:-.7px;margin:0 0 7px;color:#203d31;}
.club-header p {font-size:13px;color:#70766f;margin:0;}
.club-header a {color:#53675b;font-size:13px;text-decoration:none;border-bottom:1px solid #c7d0c8;padding-bottom:3px;}
#club-workspace {gap:28px;align-items:flex-start;}
#club-sidebar {padding:8px 0 0;gap:12px;}
#club-advisor {background:transparent;border:0;padding:0;}
#club-advisor .wrap {background:#fff;}
#club-role p {font-size:13px;line-height:1.6;color:#70766f;}
.club-services {margin:12px 0 0;}
.club-services h2 {font-size:15px;font-weight:600;margin:0 0 6px;}
.club-services dl {margin:0;}
.club-services dl > div {padding:12px 0;border-bottom:1px solid #dedfd6;}
.club-services dt {display:flex;justify-content:space-between;gap:12px;font-size:14px;line-height:1.4;}
.club-services dt span:last-child {white-space:nowrap;font-variant-numeric:tabular-nums;color:#365d49;}
.club-services dd {font-size:12px;color:#787e76;margin:5px 0 0;line-height:1.5;}
.club-services > p {font-size:12px;color:#787e76;line-height:1.7;margin:14px 0 0;}
#club-chat-panel {background:#fff;border:1px solid #dcdfd6;border-radius:12px;padding:18px 20px 16px;box-shadow:0 2px 5px #24382906;gap:8px;}
#club-chat-toolbar {align-items:center;border-bottom:1px solid #edf0e9;padding-bottom:12px;gap:12px;}
.club-chat-heading h2 {font-size:16px;font-weight:600;color:#253c30;margin:0 0 3px;}
.club-chat-heading p {font-size:12px;color:#7c827b;margin:0;}
#club-new-chat {min-height:32px;font-size:12px;box-shadow:none;}
#club-chat {background:transparent;border:0;box-shadow:none;padding:6px 0;}
#club-chat .message {font-size:14px!important;line-height:1.65;border-radius:9px;box-shadow:none;}
#club-chat .message.user {background:#eaf1e9;border:1px solid #dce7dc;color:#254330;}
#club-chat .message.bot {background:#f7f8f4;border:1px solid #ecefe5;}
#club-chat .message-buttons {opacity:.65;}
#club-chat .examples {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;width:100%;max-width:100%;}
#club-chat .example {width:auto;min-width:0;min-height:46px;padding:12px;font-size:13px;background:#fafbf7;border:1px solid #e1e5dc;border-radius:7px;box-shadow:none;}
#club-chat .example:hover {background:#f0f4ec;border-color:#b7c6b4;}
#club-message {border:1px solid #d8dfd3;border-radius:9px;background:#fff;box-shadow:0 1px 3px #24382906;}
#club-message:focus-within {border-color:#73937e;box-shadow:0 0 0 2px #e7eee5;}
#club-message textarea {background:transparent;font-size:14px;padding:12px;}
#club-message .submit-button {background:#315d48;color:#fff;border-radius:6px;padding:8px 13px;margin:5px;font-size:12px;}
#club-message .submit-button:hover {background:#244b38;}
#club-message .submit-button:disabled {opacity:.5;}
#club-settings, #club-activity {background:transparent;border:1px solid #dedfd6;border-radius:8px;box-shadow:none;}
.club-note {color:#858a81;font-size:11px;line-height:1.6;margin:12px 2px 0;}
@media (max-width:700px) {
  .gradio-container {padding:20px 16px!important;}
  .club-header {padding-bottom:16px;}
  .club-header h1 {font-size:28px;}
  .club-header > a {display:none;}
  #club-workspace {gap:20px;}
  #club-chat-panel {padding:14px;}
  #club-chat .examples {grid-template-columns:1fr;}
}
footer {display:none!important;}
"""

ROLE_LABELS = {
    "Sheriff": "Helps you choose a service and leave a contact request.",
    "Patch": "Answers questions about services, prices, and project scope.",
    "Professor Pip": "Helps beginners choose tutoring or a code review.",
}


def history_to_turns(messages):
    """Use the visible Gradio history so Undo, Retry, and Clear cannot retain hidden old turns."""
    turns, pending_user = [], None
    for message in messages:
        content = message.get("content", "")
        if isinstance(content, list):
            content = "\n".join(part.get("text", "") for part in content if isinstance(part, dict) and part.get("type") == "text")
        if not isinstance(content, str):
            continue
        if message.get("role") == "user":
            pending_user = content
        elif message.get("role") == "assistant" and pending_user is not None:
            turns.append({"user": pending_user, "assistant": content})
            pending_user = None
    return turns


def banner(persona, assignment):
    return '<div class="club-header"><div><h1>Byte Club Studio</h1>' + \
        '<p>Python tutoring, code reviews &amp; small websites.</p></div>' + \
        '<a href="mailto:hello@byteclub.example">hello@byteclub.example</a></div>'


def new_session():
    return {"history": [], "session_id": uuid.uuid4().hex, "persona": "Patch"}


def build_app(assignment="C3", runner=None, client=None):
    knowledge = load_business()
    runner = runner or (run_c4 if assignment == "C4" else run_c3)

    def chat_reply(message, visible_history, persona, explain, few_shot, location,
                   reflection, temperature, top_p, top_k, output_limit, model, session):
        session = copy.deepcopy(session or new_session())
        actual_history = history_to_turns(visible_history)
        if session["persona"] != persona:
            session = new_session()
            actual_history = []
        session["persona"] = persona
        settings = {"persona": persona, "explain": explain, "few_shot": few_shot,
                    "instruction_location": location, "reflection": reflection,
                    "temperature": temperature, "top_p": top_p, "top_k": int(top_k),
                    "max_output_tokens": int(output_limit), "model": model.strip()}
        try:
            result = runner(message, actual_history, knowledge, settings,
                            session_id=session["session_id"], client=client)
            session["history"] = result["history"]
            status = "Route: **" + result["route"] + "** · model steps: **" + str(result["model_steps"]) + "** · " + str(result["seconds"]) + " s · tokens: " + str(result["total_tokens"])
            if result["error"]:
                status += " · **Request incomplete**"
            return result["answer"], session, result["trace"], status
        except ValueError as error:
            return str(error), session, [], "Please correct the input."

    def switch_persona(persona):
        preset = PERSONAS[persona]
        session = new_session()
        session["persona"] = persona
        return (banner(persona, assignment), ROLE_LABELS[persona], preset["temperature"],
                preset["top_p"], preset["top_k"], preset["max_output_tokens"],
                session, [], [], "New conversation with **" + persona + "**.", [], [])

    theme = gr.themes.Base(primary_hue="green", neutral_hue="stone",
                           font=["Arial", "sans-serif"]).set(
        body_background_fill="#f5f4ef", body_background_fill_dark="#f5f4ef",
        body_text_color="#25332d", body_text_color_dark="#25332d",
        body_text_color_subdued="#747c72", body_text_color_subdued_dark="#747c72",
        block_background_fill="#fff", block_background_fill_dark="#fff",
        block_border_color="#dedfd6", block_border_color_dark="#dedfd6",
        block_label_text_color="#64705f", block_label_text_color_dark="#64705f",
        block_title_text_color="#53634f", block_title_text_color_dark="#53634f",
        input_background_fill="#fff", input_background_fill_dark="#fff",
        input_border_width="1px", input_border_color="#d8dfd3", input_border_color_dark="#d8dfd3",
        input_border_color_focus="#73937e", input_border_color_focus_dark="#73937e",
        button_primary_background_fill="#315d48", button_primary_background_fill_dark="#315d48",
        button_primary_background_fill_hover="#244b38", button_primary_background_fill_hover_dark="#244b38",
        button_primary_border_color="#315d48", button_primary_border_color_dark="#315d48",
        button_secondary_background_fill="#fff", button_secondary_background_fill_dark="#fff",
        button_secondary_background_fill_hover="#f0f3ec", button_secondary_background_fill_hover_dark="#f0f3ec",
        button_secondary_text_color="#49604c", button_secondary_text_color_dark="#49604c",
        button_secondary_border_color="#dce2d7", button_secondary_border_color_dark="#dce2d7",
        chatbot_text_size="14px", block_radius="8px", input_radius="7px",
    )
    with gr.Blocks(title="Byte Club Studio", fill_width=True) as app:
        header = gr.HTML(banner("Patch", assignment))
        with gr.Row(elem_id="club-workspace"):
            with gr.Column(scale=1, min_width=245, elem_id="club-sidebar"):
                persona = gr.Dropdown(list(PERSONAS), value="Patch", label="Assistant", container=False, elem_id="club-advisor")
                role = gr.Markdown(ROLE_LABELS["Patch"], elem_id="club-role")
                gr.HTML('''<section class="club-services"><h2>Services</h2><dl>
                    <div><dt><span>Python tutoring</span><span>$25 / hr</span></dt><dd>One-to-one lessons and guided practice</dd></div>
                    <div><dt><span>Code Clinic</span><span>$40 / hr</span></dt><dd>Debugging and code review</dd></div>
                    <div><dt><span>Small websites</span><span>from $300</span></dt><dd>Free 20-minute consultation</dd></div>
                    </dl><p>Online sessions in English or Arabic.<br>All prices in USD.</p></section>''')
                with gr.Accordion("Settings", open=False, elem_id="club-settings"):
                    explain = gr.Checkbox(False, label="Explain the answer", info="Include a short reason for the recommendation.")
                    few_shot = gr.Checkbox(True, label="Include worked examples", interactive=assignment == "C4")
                    location = gr.Radio(["system", "message"], value="system", label="Instruction placement", interactive=assignment == "C4")
                    reflection = gr.Checkbox(False, label="Review the reply", info="Make one extra request to check and revise the answer.")
                    model = gr.Textbox(MODEL, label="Gemini model")
                    temperature = gr.Slider(0, 1.5, value=0.15, step=0.05, label="Temperature")
                    top_p = gr.Slider(0.1, 1, value=0.75, step=0.05, label="Top-p")
                    top_k = gr.Slider(1, 64, value=20, step=1, label="Top-k")
                    output_limit = gr.Slider(1024, 4096, value=2048, step=256, label="Output token limit")
            with gr.Column(scale=3, min_width=320, elem_id="club-chat-panel"):
                with gr.Row(elem_id="club-chat-toolbar"):
                    gr.HTML('<div class="club-chat-heading"><h2>Chat</h2><p>Service questions, contact requests, and feedback.</p></div>')
                    clear = gr.Button("New chat", variant="secondary", size="sm", scale=0, min_width=88, elem_id="club-new-chat")
                session = gr.State(new_session)
                chatbot = gr.Chatbot(height=280, show_label=False, container=False, buttons=["copy_all"],
                                     render_markdown=True, allow_tags=False, elem_id="club-chat")
                message = gr.Textbox(placeholder="Write your message…", show_label=False, container=False,
                                     lines=1, max_lines=5, submit_btn="Send", stop_btn=True, elem_id="club-message")
                status = gr.Markdown("No messages yet.", render=False)
                trace = gr.JSON(label="Tool calls and results", render=False)
                chat = gr.ChatInterface(
                    fn=chat_reply, chatbot=chatbot, textbox=message,
                    additional_inputs=[persona, explain, few_shot, location, reflection,
                                       temperature, top_p, top_k, output_limit, model, session],
                    additional_outputs=[session, trace, status],
                    examples=[["How much is Python tutoring?"],
                              ["I'd like to sign up for Code Clinic."],
                              ["Feedback: the website pricing is unclear."]],
                    example_labels=["Tutoring prices", "Contact request", "Leave feedback"],
                    cache_examples=False, save_history=False, run_examples_on_click=False, autofocus=False,
                )
        with gr.Accordion("Activity", open=False, elem_id="club-activity"):
            status.render()
            trace.render()
        gr.HTML('<p class="club-note">Demo business. Contact requests are saved locally; no appointments are booked.</p>')
        outputs = [header, role, temperature, top_p, top_k, output_limit, session, chatbot, trace, status,
                   chat.chatbot_state, chat.chatbot_value]
        persona.change(switch_persona, inputs=[persona], outputs=outputs, queue=False)
        clear.click(switch_persona, inputs=[persona], outputs=outputs, queue=False)
        chatbot.clear(lambda: (new_session(), [], "New conversation."), outputs=[session, trace, status], queue=False)
    # Gradio 6 accepts theme and CSS on launch rather than Blocks construction.
    app.byteclub_launch = {"theme": theme, "css": CSS}
    return app
