from    flask               import  request, jsonify    # type: ignore
from    .database           import  create_connection   # type: ignore
from    mysql.connector     import  Error               # type: ignore
from    json                import  loads
import  os

API_TOKEN                               =   os.getenv("API_TOKEN")
UPLOAD_FOLDER                           =   os.getenv("UPLOAD_FOLDER")
UPLOAD_FOLDER                           =   os.path.abspath(UPLOAD_FOLDER)

def validate_token(token):
    return token == API_TOKEN

def setup_routes(app):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER']         =   UPLOAD_FOLDER

    @app.route('/captacao/login/', methods=['POST'], scrict_slashed=False)
    def login():
        api_token                       =   data.get('apiToken')
        if not validate_token(api_token):
            return jsonify({"error": "Token inválido"}), 403

        data                            =   request.json
        if not data:
            return jsonify({"error": "Requisição sem body"}), 400

        print(f"jsonLogin: {data}")

        table_name                      =   data.get('tableName')
        name                            =   data.get('nome')
        password                        =   data.get('senha')
        if not api_token or not table_name or not name or not password:
            return jsonify({"error": "Campos faltando no JSON"}), 400

        connection                      =   create_connection()
        if connection:
            try:
                cursor                  =   connection.cursor()
                query                   =   f"""
                    SELECT 	    *
                    FROM 	    {table_name}
                    WHERE 	    nome 	= 	%s
                    AND 	    senha 	= 	%s
                    AND 	    del 	!= 	'1'
                """
                cursor.execute(query, (name, password))
                dados                   =   cursor.fetchone()

                print(f"queryLogin: {query}")

                if dados:
                    column_names        =   [desc[0] for desc in cursor.description]
                    response            =   {"data": dict(zip(column_names, dados))}
                else:
                    response            =   {"error": "Usuário não encontrado ou senha incorreta."}
            except Error as e:
                response                =   {"error": str(e)}
            finally:
                cursor.close()
                connection.close()
        else:
            response                    =   {"error": "Não foi possível conectar ao banco de dados."}

        return jsonify(response)

    @app.route('/captacao/select/', defaults={'id': None}, methods=['GET'], scrict_slashed=False)
    @app.route('/captacao/select/<int:id>', methods=['GET'], scrict_slashed=False)
    def get_data(id):
        api_token                       =   data.get('apiToken')
        if not validate_token(api_token):
            return jsonify({"error": "Token inválido"}), 403

        if id is None:
            return jsonify({"error": "ID não foi passado na URL"}), 400

        data                            =   request.json
        if not data:
            return jsonify({"error": "Requisição sem body"}), 400

        print(f"jsonSelect: {data}")

        table_name                      =   data.get('tableName')
        field_id                        =   data.get('fieldId')
        if not table_name or not field_id:
            return jsonify({"error": "Campos faltando no JSON"}), 400

        connection                      =   create_connection()
        if connection:
            try:
                cursor                  =   connection.cursor(dictionary=True)
                if table_name           ==  "contatos" or table_name == "contatos_":
                    if id is not None:
                        query           =   f"""
                            SELECT      *
                            FROM        {table_name}
                            WHERE       id      =   %s
                        """
                        print(f"qCont: {query}")
                        cursor.execute(query, (id,))
                    else:
                        query           =   f"""
                            SELECT      *
                            FROM        {table_name}
                        """
                        print(f"qContnoId: {query}")
                        cursor.execute(query)
                else:
                    if id is not None:
                        query           =   f"""
                            SELECT      *
                            FROM        {table_name}
                            WHERE       {field_id}  	= 	%s
                            AND 		del  	        != 	'1'
                        """
                        print(f"querySelectId: {query}")
                        cursor.execute(query, (id,))
                    else:
                        query           =   f"""
                            SELECT      *
                            FROM        {table_name}
                            WHERE       del     !=  '1'
                        """
                        print(f"querySelect: {query}")
                        cursor.execute(query)

                dados                   =   cursor.fetchall()
                response                =   {"data": dados}
            except Error as e:
                response                =   {"error": str(e)}
            finally:
                cursor.close()
                connection.close()
        else:
            response                    =   {"error": "Não foi possível conectar ao banco de dados."}

        return jsonify(response)

    @app.route('/captacao/info-geral/<int:id>', methods=['GET'], scrict_slashed=False)
    def get_info(id):
        api_token                       =   data.get('apiToken')
        if not validate_token(api_token):
            return jsonify({"error": "Token inválido"}), 403

        if id is None:
            return jsonify({"error": "ID não foi passado na URL"}), 400

        data                            =   request.json
        print(f"jsonInfo: {data}")

        connection                      =   create_connection()
        if connection:
            cursor                      =   connection.cursor()
            try:
                query                   =   f"""
                    SELECT		cont.nome				AS	'indicador'	,
                                cont.numero				AS	'numero'	,
                                imoveis_.*								,
                                prop.*
                    FROM		imoveis_
                    INNER JOIN 	r_PropImovel_ 			AS	rel
                    ON			imoveis_.codImovel		=	rel.codImovel
                    INNER JOIN	proprietarios_			AS	prop
                    ON			rel.codProprietario		=	prop.codProprietario
                    INNER JOIN	contatos_				AS	cont
                    ON			cont.codImovel			=	imoveis_.codImovel
                    WHERE		imoveis_.codImovel		=	{id}
                    AND			imoveis_.del			!=	'1'
                    AND			prop.del				!=	'1'
                    AND			rel.del					!=	'1'
                """

                print(f"queryInfo: {query}")
                cursor.execute(query)
                dados                   =   cursor.fetchone()
                if dados:
                    column_names        =   [desc[0] for desc in cursor.description]
                    response            =   {"data": dict(zip(column_names, dados))}
                else:
                    return jsonify({"error": f"Não existe imóvel com esse ID ({id})"}), 403

                cursor.close()
                connection.close()
            except Error as e:
                response                =   {"error": str(e)}
            finally:
                cursor.close()
                connection.close()

        else:
            response                    =   {"error": "Não foi possível conectar ao banco de dados."}

        return jsonify(response)

    @app.route('/captacao/insert/', methods=['POST'], scrict_slashed=False)
    def create_data():
        api_token                       =   data.get('apiToken')
        if not validate_token(api_token):
            return jsonify({"error": "Token inválido"}), 403

        data                            =   request.json
        print(f"jsonInsert: {data}")

        table_name                      =   data.get('tableName')
        field_id                        =   data.get('fieldId')
        if not table_name or not field_id:
            return jsonify({"error": "Campos faltando no JSON"}), 400

        connection                      =   create_connection()
        if connection:
            dados                       =   data.get(table_name)
            camposQuery                 =   dados[0].keys()

            for dado in dados:
                # Create the query and put the fields of table automatic #
                campos_str              =   ', '.join(camposQuery)
                valores_str             =   ', '.join([f"'{dado[campo]}'" for campo in camposQuery])

                query = f"""
                INSERT INTO             {table_name} ({campos_str})
                VALUES                  ({valores_str})
                """

                print(f"queryInsert: {query}")
                cursor                  =   connection.cursor()
                try:
                    cursor.execute(query)
                    connection.commit()

                    # Return the id #
                    rQuery              =   f"""
                    SELECT		        *
                    FROM		        {table_name}
                    ORDER BY	        {field_id}	DESC
                    LIMIT	            1
                    """

                    print(f"rQuery: {rQuery}")
                    cursor.execute(rQuery)
                    dados               =   cursor.fetchone()
                    column_names        =   [desc[0] for desc in cursor.description]
                    response            =   {"data": dict(zip(column_names, dados))}
                except Error as e:
                    response            =   {"error": str(e)}

            cursor.close()
            connection.close()
        else:
            response                    =   {"error": "Não foi possível conectar ao banco de dados."}

        return jsonify(response)

    @app.route('/captacao/update/<int:id>', methods=['PUT'], scrict_slashed=False)
    def update_data(id):
        api_token                       =   data.get('apiToken')
        if not validate_token(api_token):
            return jsonify({"error": "Token inválido"}), 403

        if id is None:
            return jsonify({"error": "ID não foi passado na URL"}), 400

        data                            =   request.json
        print(f"jsonUpdate: {data}")

        table_name                      =   data.get('tableName')
        field_id                        =   data.get('fieldId')
        update_fields                   =   data.get('updateFields')
        if not table_name or not field_id or not update_fields:
            return jsonify({"error": "Campos faltando no JSON"}), 400

        set_clause                      =   ', '.join([f"{key} = '{value}'" for key, value in update_fields.items()])
        connection                      =   create_connection()
        if connection:
            query                       =   f"""
                UPDATE                  {table_name}
                SET                     {set_clause}
                WHERE                   {field_id}      =   {id}
            """

            print(f"queryUpdate: {query}")
            cursor                      =   connection.cursor()
            try:
                cursor.execute(query)
                connection.commit()
                response                =   {"message": "Registro atualizado com sucesso!"}
            except Error as e:
                response                =   {"error": str(e)}
            finally:
                cursor.close()
                connection.close()
        else:
            response                    =   {"error": "Não foi possível conectar ao banco de dados."}

        return jsonify(response)

    @app.route('/captacao/delete/<int:id>', methods=['DELETE'], scrict_slashed=False)
    def delete_data(id):
        api_token                       =   data.get('apiToken')
        if not validate_token(api_token):
            return jsonify({"error": "Token inválido"}), 403

        if id is None:
            return jsonify({"error": "ID não foi passado na URL"}), 400

        data                            =   request.json
        print(f"jsonDelete: {data}")

        table_name                      =   data.get('tableName')
        field_id                        =   data.get('fieldId')
        if not table_name or not field_id:
            return jsonify({"error": "Campos faltando no JSON"}), 400

        connection                      =   create_connection()
        if connection:
            query                       =   f"""
                UPDATE                  {table_name}
                SET                     del             =   '1'
                WHERE                   {field_id}      =   {id}
            """

            print(f"queryDelete: {query}")
            cursor                      =   connection.cursor()
            try:
                cursor.execute(query)
                connection.commit()
                response                =   {"message": "Registro deletado com sucesso!"}
            except Error as e:
                response                =   {"error": str(e)}
            finally:
                cursor.close()
                connection.close()
        else:
            response                    =   {"error": "Não foi possível conectar ao banco de dados."}

        return jsonify(response)

    @app.route('/captacao/upload', methods=['POST'], scrict_slashed=False)
    def upload():
        if 'data' not in request.form:
            return jsonify({'error': 'JSON data is missing'}), 400

        json_data = request.form['data']
        try:
            json_data = loads(json_data)
        except ValueError as e:
            return jsonify({'error': 'Invalid JSON'}), 400

        try:
            files = request.files
            for key in files:
                file = files[key]
                filename = file.filename
                file.save(os.path.join(UPLOAD_FOLDER, filename))

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'Invalid files'}), 400

        return jsonify({'status': 'success'}), 200
