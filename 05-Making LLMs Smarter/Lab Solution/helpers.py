from openai import OpenAI
import base64, sqlite3, json, re, os

IMAGE_PATH = 'Data/visual.png'

def answer_question_textually(input):
    print('Calling text2sql()')
    sql = text2sql(input)
    print('Calling execute_sql()')
    result = execute_sql(sql)
    return json.dumps(result)

textual_response_tool = {
    'type': 'function',
    'function': {
        'name': 'answer_question_textually',
        'description': '''
            Queries the Chinook database to answer a question and provide a
            textual response. Only call this function if the question doesn't
            lend itself to a graphical response. Examples include "How many
            employees does Chinook have" and "How much revenue did Chinook
            generate in 2011."
            ''',
        'parameters': {
            'type': 'object',
            'properties': {
                'input': {
                    'type': 'string',
                    'description': 'Input from the user'
                }
            },
            'required': ['input']
        }
    }
}

def answer_question_visually(input):
    sql = text2sql(input)
    result = execute_sql(sql)
    print('Calling text2code()')
    code = text2code(input, json.dumps(result))
    print('Executing code')
    exec(code) # Execute the LLM-generated code
    url = get_data_url(IMAGE_PATH)
    os.remove(IMAGE_PATH)
    return url

data_visualization_tool = {
    'type': 'function',
    'function': {
        'name': 'answer_question_visually',
        'description': '''
            Queries the Chinook database to answer a question and provide a
            visual response in the form of a chart or graph. Only call this
            function if the question lends itself to a graphical response.
            Examples include "Plot sales of Chinook's 10 most popular albums"
            and "Show me how many albums were sold in 2010, 2011, and 2012."
            ''',
        'parameters': {
            'type': 'object',
            'properties': {
                'input': {
                    'type': 'string',
                    'description': 'Input from the user'
                }
            },
            'required': ['input']
        }
    }
}

def text2sql(text):
    prompt = f'''
        Generate a well-formed SQLite query from the prompt below. Return
        the SQL only. Do not use markdown formatting, and do not use SELECT *.

        PROMPT: {text}
    
        The database targeted by the query contains the following tables:

        CREATE TABLE "albums" (
            [AlbumId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [Title] NVARCHAR(160) NOT NULL,
            [ArtistId] INTEGER NOT NULL,
            FOREIGN KEY ([ArtistId]) REFERENCES "artists" ([ArtistId])
                ON DELETE NO ACTION ON UPDATE NO ACTION
        );

        CREATE TABLE "artists" (
            [ArtistId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [Name] NVARCHAR(120)
        );

        CREATE TABLE "customers" (
            [CustomerId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [FirstName] NVARCHAR(40) NOT NULL,
            [LastName] NVARCHAR(20) NOT NULL,
            [Company] NVARCHAR(80),
            [Address] NVARCHAR(70),
            [City] NVARCHAR(40),
            [State] NVARCHAR(40),
            [Country] NVARCHAR(40),
            [PostalCode] NVARCHAR(10),
            [Phone] NVARCHAR(24),
            [Fax] NVARCHAR(24),
            [Email] NVARCHAR(60) NOT NULL,
            [SupportRepId] INTEGER,
            FOREIGN KEY ([SupportRepId]) REFERENCES "employees" ([EmployeeId])
                ON DELETE NO ACTION ON UPDATE NO ACTION
        );

        CREATE TABLE "employees" (
            [EmployeeId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [LastName] NVARCHAR(20) NOT NULL,
            [FirstName] NVARCHAR(20) NOT NULL,
            [Title] NVARCHAR(30),
            [ReportsTo] INTEGER,
            [BirthDate] DATETIME,
            [HireDate] DATETIME,
            [Address] NVARCHAR(70),
            [City] NVARCHAR(40),
            [State] NVARCHAR(40),
            [Country] NVARCHAR(40),
            [PostalCode] NVARCHAR(10),
            [Phone] NVARCHAR(24),
            [Fax] NVARCHAR(24),
            [Email] NVARCHAR(60),
            FOREIGN KEY ([ReportsTo]) REFERENCES "employees" ([EmployeeId])
                ON DELETE NO ACTION ON UPDATE NO ACTION
        );

        CREATE TABLE "genres" (
            [GenreId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [Name] NVARCHAR(120)
        );

        CREATE TABLE "invoice_items" (
            [InvoiceLineId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [InvoiceId] INTEGER NOT NULL,
            [TrackId] INTEGER NOT NULL,
            [UnitPrice] NUMERIC(10, 2) NOT NULL,
            [Quantity] INTEGER NOT NULL,
            FOREIGN KEY ([InvoiceId]) REFERENCES "invoices" ([InvoiceId])
                ON DELETE NO ACTION ON UPDATE NO ACTION,
            FOREIGN KEY ([TrackId]) REFERENCES "tracks" ([TrackId])
                ON DELETE NO ACTION ON UPDATE NO ACTION
        );

        CREATE TABLE "invoices" (
            [InvoiceId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [CustomerId] INTEGER NOT NULL,
            [InvoiceDate] DATETIME NOT NULL,
            [BillingAddress] NVARCHAR(70),
            [BillingCity] NVARCHAR(40),
            [BillingState] NVARCHAR(40),
            [BillingCountry] NVARCHAR(40),
            [BillingPostalCode] NVARCHAR(10),
            [Total] NUMERIC(10, 2) NOT NULL,
            FOREIGN KEY ([CustomerId]) REFERENCES "customers" ([CustomerId])
                ON DELETE NO ACTION ON UPDATE NO ACTION
        );

        CREATE TABLE "media_types" (
            [MediaTypeId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [Name] NVARCHAR(120)
        );

        CREATE TABLE "playlist_track" (
            [PlaylistId] INTEGER NOT NULL,
            [TrackId] INTEGER NOT NULL,
            PRIMARY KEY ([PlaylistId], [TrackId]),
            FOREIGN KEY ([PlaylistId]) REFERENCES "playlists" ([PlaylistId])
                ON DELETE NO ACTION ON UPDATE NO ACTION,
            FOREIGN KEY ([TrackId]) REFERENCES "tracks" ([TrackId])
                ON DELETE NO ACTION ON UPDATE NO ACTION
        );

        CREATE TABLE "playlists" (
            [PlaylistId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [Name] NVARCHAR(120)
        );

        CREATE TABLE "tracks" (
            [TrackId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [Name] NVARCHAR(200) NOT NULL,
            [AlbumId] INTEGER,
            [MediaTypeId] INTEGER NOT NULL,
            [GenreId] INTEGER,
            [Composer] NVARCHAR(220),
            [Milliseconds] INTEGER NOT NULL,
            --[Bytes] INTEGER,
            [UnitPrice] NUMERIC(10, 2) NOT NULL,
            FOREIGN KEY ([AlbumId]) REFERENCES "albums" ([AlbumId])
                ON DELETE NO ACTION ON UPDATE NO ACTION,
            FOREIGN KEY ([MediaTypeId]) REFERENCES "media_types" ([MediaTypeId])
                ON DELETE NO ACTION ON UPDATE NO ACTION,
            FOREIGN KEY ([GenreId]) REFERENCES "genres" ([GenreId])
                ON DELETE NO ACTION ON UPDATE NO ACTION
        );
        '''

    messages = [
        {
            'role': 'system',
            'content': 'You are a database expert who can convert questions into SQL queries'
        },
        {
            'role': 'user',
            'content': prompt
        }
    ]

    client = OpenAI()
    
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        temperature=0
    )

    sql = response.choices[0].message.content

    # Strip markdown characters if present
    pattern = r'^```[\w]*\n|\n```$'
    return re.sub(pattern, '', sql, flags=re.MULTILINE)

def execute_sql(sql):
    connection = sqlite3.connect('data/chinook.db')
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

def text2code(text, data):
    prompt = f'''
        Generate Python code that uses Matplotlib and optionally Seaborn to generate
        a chart or graph in response to the prompt below using the date below. Return
        the code only. Do not use markdown formatting, and do not explain the code.
        Do not generate code that could be harmful to the computer it's running on,
        and do not include a call to plt.show(). Include code to save the image that
        is generated as a PNG file using the path "{IMAGE_PATH}". Include a call to
        plt.close() at the end, and a call to matplotlib.use('Agg') at the beginning.
        Also include code to suppress any warnings.

        PROMPT: {text}

        DATA: {data}
        '''

    messages = [
        {
            'role': 'system',
            'content': '''
                You are a data expert who can respond to questions by generating
                code that creates colorful charts and graphs.
                '''
        },
        {
            'role': 'user',
            'content': prompt
        }
    ]

    client = OpenAI()
    
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        temperature=0
    )

    code = response.choices[0].message.content

    # Strip markdown characters if present
    pattern = r'^```[\w]*\n|\n```$'
    return re.sub(pattern, '', code, flags=re.MULTILINE)

def get_data_url(image_path):
    with open(image_path, 'rb') as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode('utf-8')

    return f'data:image/png;base64,{encoded_string}'

def chat(input, messages=None):
    if not messages:
        instructions = '''
            You are a helpful assistant who can answer questions and generate charts and graphs
            from the Chinook database. The database contains information about the Chinook digital
            media store. It contains tables with information about customers, invoices, employees,
            aetists, and more. The data schema supports scenarios like querying customer purchase
            history, exploring music genres, managing playlists, and handling employee reporting
            structures. The database contains the following tables:

            employees - Information about employees of Chinook
            customers - Information about customers who purchase Chinook products
            invoices - Information about invoices, including customer and invoice date
            invoice_items - Line items for invoices in the "invoices" table
            artists - Information about artists in the Chinook catalog
            media_types - Media types such as MPEG audio and AAC audio
            genres - Stores music genres such as rock, metal, and jazz
            albums - Stores albums, which are collections of tracks
            tracks - Tracks for the albums in the "albums" table
            playlists - Stores playlists, which are collections of playlist tracks
            playlist_tracks - Tracks for the playlists in the "playlists" table

            Only answer questions that can be answered by querying the database. If asked a
            question that can't be answered by a database query, say "I don't know." Do not
            use markdown formatting.
            '''

        messages = [{ 'role': 'system', 'content': instructions }]
    
    message = { 'role': 'user', 'content': input }
    messages.append(message)

    # Call the LLM
    client = OpenAI()
    
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        tools=[textual_response_tool, data_visualization_tool]
    )
    
    # If one or more tool calls are required, execute them
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
    
            if function_name == 'answer_question_textually':
                input = json.loads(tool_call.function.arguments)['input']
                print('Calling answer_question_textually()')
                output = answer_question_textually(input)
                messages.append({ 'role': 'function', 'name': function_name, 'content': output })

            elif function_name == 'answer_question_visually':
                input = json.loads(tool_call.function.arguments)['input']
                print(f'Calling answer_question_visually()')
                output = answer_question_visually(input)
                messages.append({ 'role': 'assistant', 'content': output })
                return messages # Early exit with image URL

            else:
                raise Exception('Invalid function name')
    
        # Pass the function output to the LLM
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages
        )
    
    # Return a message thread containing the LLM's response
    messages.append({ 'role': 'assistant', 'content': response.choices[0].message.content })
    return messages