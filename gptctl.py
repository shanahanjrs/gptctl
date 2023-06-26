import json

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import DuckDuckGoSearchRun, Tool
from langchain.memory import ConversationBufferMemory

# suppress known DDG Plugin warnings
import warnings
warnings.filterwarnings('ignore')


def menu():
    """
    Prints out the main menu on startup
    :return: None
    """
    print("""    +------------------------------------------------------------+
    | You can chat with ChatGPT via your command line here.      |
    | use `:wiki` to test the Wikipedia plugin                   |
    | use `:leo` to test the Search Engine and Math plugins      |
    | use `:quit` to stop                                        |
    +------------------------------------------------------------+""")


def colorize(color, text):
    """
    Takes a color name and some text and returns the text in the specified color for cli output
    :param color: (str) green or blue for now
    :param text: (str) string to be colorized for cli output
    :return: str
    """
    color = color.lower()

    colors = {
        'green': '\033[92m{}\033[0m',
        'blue': '\033[94m{}\033[0m'
    }

    if color not in colors.keys():
        print(f'ERROR: Invalid color choice [{color}]')
        exit(1)

    return colors[color].format(text)


def main():
    ps1 = colorize('green', 'λ')
    menu()

    api_key = json.load(open('config.json'))['API_KEY']

    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=api_key,
        model_name="gpt-3.5-turbo"
    )
    memory = ConversationBufferMemory(
        input_key="input"
    )

    ddg = DuckDuckGoSearchRun()
    tools = [
        Tool(
            name="Search",
            func=ddg.run,
            description="useful for when you need to answer questions or search the internet",
        )
    ]

    chat = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=False,
    )

    while True:
        inp = input(f'{ps1} ')

        if inp == '':
            continue

        if inp.lower() == ':wiki':
            inp = 'can you give me a summary of the first paragraph for the wikipedia entry for ChatGPT'
            print(f'{ps1} {inp}')

        if inp.lower() == ':leo':
            inp = 'Who is Leonardo DiCaprio\'s girlfriend and what is her current age raised to the 0.43 power?'
            print(f'{ps1} {inp}')

        if inp.lower() in [':quit', ':exit', 'quit', 'exit']:
            print('Goodbye!')
            exit(0)

        try:
            resp = chat({"input": inp, "chat_history": memory.chat_memory.messages})
        except Exception as e:
            print(f'Whoops! We ran into an exception. Would you like me to show it to you?')
            if input(colorize('green', '[Y/n] ')).lower() == 'n':
                continue
            print(e)
            print("\n")
            continue

        print(colorize('blue', resp['output']))


if __name__ == '__main__':
    main()
