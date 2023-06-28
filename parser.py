from anytree import Node, RenderTree


def string_normalize(string, longinus=10):
    return string + (" "*(longinus-len(string)))

#Inicializamos arbol
def render_tree(root: object) -> None:
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))


def code_translate(root: object, file, tabs = 0) -> None:
    f = open(file, 'a')
    if True == "PRINT":
        print_statement = "print("
        for i in root.children:
            for j in i.children:
                print_statement += j.name
        f.write("\t"*tabs+print_statement+")"+"\n")
        f.close()

    if root.name == "=":
        assignment_statement = ""
        for i in root.children:
            if i.name != "expression":
                assignment_statement += i.name + " = "
            else:
                for j in i.children:
                    if len(j.name) < 15:
                        assignment_statement += j.name + " "
                    else:
                        assignment_statement += j.name + "\n "

        f.write("\t"*tabs+assignment_statement+"\n")
        f.close()
    
    if root.name == "for":
        for_statement = "for "
        for i in root.children:
            if i.name == "iterable":
                for j in i.children:
                    for_statement += j.name + " "
            elif i.name == "statements":
                f.write(for_statement+":"+"\n")
                f.close()
                for j in i.children:
                    code_translate(j, file, tabs + 1)
            elif i.name not in ["{","}"]:
                for_statement += i.name + " "
        
    if root.name == "if":
        if_statement = "if "
        for i in root.children:
            if i.name == "expression":
                for j in i.children:
                    if_statement += j.name + " "
            elif i.name == "statements":
                f.write("\t"*tabs+if_statement+":"+"\n")
                f.close()
                for j in i.children:
                    code_translate(j, file, tabs + 1)
            elif i.name == "else":
                code_translate(i, file)
        
    if root.name == "else":
        else_statement = "else:"
        for i in root.children:
            if i.name == "statements":
                f.write("\t"*tabs+else_statement+"\n")
                f.close()
                for j in i.children:
                    code_translate(j, file, tabs + 1)
        
    
    if root.name == "statements":
        for i in root.children:
            code_translate(i, file)



class parser:
    def __init__(self, it):
        # define sync set
        self.sync_set = ["PRINT", "FOR", "IF", "$"]

        # set i/o
        self.input_tokens = it
        self.output_errors = []

        # set process variables
        self.arbol = None
        self.current_node = None
        self.current_token = ""
        self.current_token_value = ""
        self.next_token()


    #Evaluamos el siguiente token
    def next_token(self):
        self.current_token = self.input_tokens.pop(0)

    #Añadimos los errores a una lista
    def add_error(self, error, symbol, at):
        self.output_errors.append(string_normalize(
            error, 19)+" "+string_normalize("\""+symbol+"\"", 16)+", at "+at)

    def synchronize(self):
        while self.current_token not in self.sync_set:
            self.next_token()


    def Program(self):
        self.arbol = Node("statements")
        self.nodo_actual = self.arbol
        if self.StatementList(self.nodo_actual):
            if self.current_token == "$":
                return True
            # else:
            #     self.add_error("Se esperaba un token"COMMA"$"COMMA"final")
        return False

    def StatementList(self, node):
        if self.Statement(node):
            if self.StatementList(node):
                return True
        if self.current_token in ["$", "RKEY"]:
            return True
        return False

    def Statement(self, node):
        if self.current_token == "PRINT":
            if self.PrintStatement(node):
                return True
        elif self.current_token == "ID":
            if self.AssignmentStatement(node):
                return True
        elif self.current_token == "FOR":
            if self.ForStatement(node):
                return True
        elif self.current_token == "IF":
            if self.IfStatement(node):
                return True
        return False

    def PrintStatement(self, node):
        if self.current_token == "PRINT":
            # print_node = Node("PRINT", parent=self.arbol)
            print_node = Node("PRINT", parent=node)
            self.next_token()
            if self.current_token == "LBRACKET":
                aux_node = Node("LBRACKET", parent=print_node)
                self.next_token()
                aux_node = Node("expression", parent=print_node)
                if self.Expression(aux_node):
                    if self.current_token == "RBRACKET":
                        aux_node = Node("RBRACKET", parent=print_node)
                        self.next_token()
                        return True
                    else:
                        self.add_error("Se esperaba un token", "RBRACKET",
                                       "print statement")
                else:
                    self.add_error("Se esperaba una expression",
                                   "any printable", "print statement")
            else:
                self.add_error("Se esperaba un token", "LBRACKET", "print statement")
        return False

    def AssignmentStatement(self, node):
        if self.current_token == "ID":
            assignment_node = Node("ASSIGN_VAR", parent=node)
            aux_node = Node("ID", parent=assignment_node)
            self.next_token()
            if self.current_token == "ASSIGN_VAR":
                aux_node = Node("expression", parent=assignment_node)
                self.next_token()
                if self.Expression(aux_node):
                    return True
                else:
                    self.add_error("Se esperaba una expression",
                                   "any varible", "assignment statement")
            else:
                self.add_error("Se esperaba un token", "ASSIGN_VAR", "assignment statement")
        return False

    def ForStatement(self, node):
        if self.current_token == "FOR":
            for_node = Node("FOR", parent=node)
            self.next_token()
            if self.current_token == "ID":
                aux_node = Node("ID", parent=for_node)
                self.next_token()
                if self.current_token == "IN":
                    aux_node = Node("IN", parent=for_node)
                    self.next_token()
                    aux_node = Node("iterable", parent=for_node)
                    if self.Iterable(aux_node):
                        if self.current_token == "LKEY":
                            aux_node = Node("LKEY", parent=for_node)
                            self.next_token()
                            aux_node = Node("statements", parent=for_node)
                            self.nodo_actual = aux_node
                            if self.StatementList(self.nodo_actual):
                                if self.current_token == "RKEY":
                                    aux_node = Node("RKEY", parent=for_node)
                                    self.next_token()
                                    return True
                                else:
                                    self.add_error(
                                        "Se esperaba un token", "RKEY", "for statement")
                        else:
                            self.add_error("Se esperaba un token",
                                           "LKEY", "for statement")
                    else:
                        self.add_error("Se esperaba una list",
                                       "any iterable", "for statement")
                else:
                    self.add_error("Se esperaba un token", "IN", "for statement")
            else:
                self.add_error("Se esperaba un id", "any varible", "for statement")
        return False

    def IfStatement(self, node):
        if self.current_token == "IF":
            if_node = Node("IF", parent=node)
            self.next_token()
            aux_node = Node("expression", parent=if_node)
            if self.Expression(aux_node):
                if self.current_token == "LKEY":
                    aux_node = Node("LKEY", parent=if_node)
                    self.next_token()
                    aux_node = Node("statements", parent=if_node)
                    self.nodo_actual = aux_node
                    if self.StatementList(self.nodo_actual):
                        if self.current_token == "RKEY":
                            aux_node = Node("RKEY", parent=if_node)
                            self.next_token()
                            if self.ElseStatement(if_node):
                                return True
                        else:
                            self.add_error("Se esperaba un token",
                                           "RKEY", "if statement")
                else:
                    self.add_error("Se esperaba un token", "LKEY", "if statement")
            else:
                self.add_error("Se esperaba una expression",
                               "any boolean", "if statement")
        return False

    def Iterable(self, node):
        if self.current_token == "ID":
            self.next_token()
            return True
        if self.List(node):
            return True
        return False

    def ElseStatement(self, node):
        if self.current_token == "ELSE":
            else_node = Node("ELSE", parent=node)
            self.next_token()
            if self.current_token == "LKEY":
                aux_node = Node("RKEY", parent=else_node)
                self.next_token()
                aux_node = Node("statements", parent=else_node)
                self.nodo_actual = aux_node
                if self.StatementList(self.nodo_actual):
                    if self.current_token == "RKEY":
                        aux_node = Node("RKEY", parent=else_node)
                        self.next_token()
                        return True
                    else:
                        self.add_error("Se esperaba un token", "RKEY", "else statement")
            else:
                self.add_error("Se esperaba un token", "LKEY", "else statement")
        if self.current_token in ["$", "PRINT", "ID", "FOR", "IF", "RKEY"]:
            return True
        return False

    def ComparisonOperator(self, node):
        if self.current_token == "EQUAL":
            aux_node = Node("EQUAL", parent=node)
            self.next_token()
            return True
        if self.current_token == "DIFERENT":
            aux_node = Node("DIFERENT", parent=node)
            self.next_token()
            return True
        if self.current_token == "LT":
            aux_node = Node("LT", parent=node)
            self.next_token()
            return True
        if self.current_token == "GT":
            aux_node = Node("GT", parent=node)
            self.next_token()
            return True
        if self.current_token == "LTE":
            aux_node = Node("LTE", parent=node)
            self.next_token()
            return True
        if self.current_token == "GTE":
            aux_node = Node("GTE", parent=node)
            self.next_token()
            return True
        return False

    def BoolValue(self, node):
        if self.current_token == "FALSE":
            aux_node = Node("FALSE", parent=node)
            self.next_token()
            return True
        if self.current_token == "TRUE":
            aux_node = Node("TRUE", parent=node)
            self.next_token()
            return True
        return False

    def List(self, node):
        if self.current_token == "LCOL":
            aux_node = Node("LCOL", parent=node)
            self.next_token()
            if self.ExpressionList(node):
                if self.current_token == "RCOL":
                    aux_node = Node("RCOL", parent=node)
                    self.next_token()
                    return True
                else:
                    self.add_error("Se esperaba un token", "RCOL", "list expression")
        return False

    def ExpressionList(self, node):
        if self.Expression(node):
            if self.ExpressionListTail(node):
                return True
        if self.current_token == "RCOL":
            return True
        return False

    def ExpressionListTail(self, node):
        if self.current_token == "COMMA":
            self.next_token()
            if self.Expression(node):
                if self.ExpressionListTail(node):
                    return True
        if self.current_token == "RCOL":
            return True
        return False

    def Expression(self, node):
        if self.OrExpression(node):
            if self.ExpressionPrima(node):
                return True
        return False

    def ExpressionPrima(self, node):
        if self.current_token == "AND":
            aux_node = Node("AND", parent=node)
            self.next_token()
            if self.OrExpression(node):
                if self.ExpressionPrima(node):
                    return True
        if self.current_token in ["RBRACKET", "$", "PRINT", "ID", "FOR", "IF", "LKEY", "COMMA", "RKEY"]:
            return True
        return False

    def OrExpression(self, node):
        if self.NotExpression(node):
            if self.OrExpressionPrima(node):
                return True
        return False

    def OrExpressionPrima(self, node):
        if self.current_token == "OR":
            aux_node = Node("OR", parent=node)
            self.next_token()
            if self.NotExpression(node):
                if self.OrExpressionPrima(node):
                    return True
        if self.current_token in ["RBRACKET", "$", "PRINT", "ID", "FOR", "IF", "LKEY", "COMMA", "AND", "RKEY"]:
            return True
        return False

    def NotExpression(self, node):
        if self.current_token == "not":
            self.next_token()
            if self.ComparisonExpression(node):
                return True
        if self.ComparisonExpression(node):
            return True
        return False

    def ComparisonExpression(self, node):
        if self.IntExpression(node):
            if self.ComparisonExpressionPrima(node):
                return True
        return False

    def ComparisonExpressionPrima(self, node):
        if self.ComparisonOperator(node):
            if self.IntExpression(node):
                return True
        if self.current_token in ["RBRACKET", "$", "PRINT", "ID", "FOR", "IF", "LKEY", "COMMA", "AND", "OR", "RKEY"]:
            return True
        return False

    def IntExpression(self, node):
        if self.Term(node):
            if self.IntExpressionPrima(node):
                return True
        return False

    def IntExpressionPrima(self, node):
        if self.current_token == "PLUS":
            aux_node = Node("PLUS", parent=node)
            self.next_token()
            if self.Term(node):
                if self.IntExpressionPrima(node):
                    return True
        if self.current_token == "MINUS":
            aux_node = Node("MINUS", parent=node)
            self.next_token()
            if self.Term(node):
                if self.IntExpressionPrima(node):
                    return True
        if self.current_token in ["RBRACKET", "$", "PRINT", "ID", "FOR", "IF", "LKEY", "COMMA", "AND", "OR", "EQUAL", "DIFERENT", "LT", "GT", "LTE", "GTE", "RKEY"]:
            return True
        return False

    def Term(self, node):
        if self.Factor(node):
            if self.TermPrima(node):
                return True
        return False

    def TermPrima(self, node):
        if self.current_token == "MULT":
            aux_node = Node("MULT", parent=node)
            self.next_token()
            if self.Factor(node):
                if self.TermPrima(node):
                    return True
        if self.current_token == "DIV":
            aux_node = Node("DIV", parent=node)
            self.next_token()
            if self.Factor(node):
                if self.TermPrima(node):
                    return True
        if self.current_token in ["RBRACKET", "$", "PRINT", "ID", "FOR", "IF", "LKEY", "COMMA", "AND", "OR", "EQUAL", "DIFERENT", "LT", "GT", "LTE", "GTE", "PLUS", "MINUS", "RKEY"]:
            return True
        return False

    def Factor(self, node):
        if self.current_token == "LBRACKET":
            factor_node = Node("LBRACKET", parent=node)
            self.next_token()
            if self.Expression(node):
                if self.current_token == "RBRACKET":
                    factor_node = Node("RBRACKET", parent=node)
                    return True
                else:
                    self.add_error("Se esperaba un token", "RBRACKET", "factor expression")
        if self.current_token == "ID":
            factor_node = Node("ID", parent=node)
            self.next_token()
            return True
        if self.current_token == "INTEGER_CONST":
            factor_node = Node("INTEGER_CONST", parent=node)
            self.next_token()
            return True
        if self.current_token == "STRING_LITERAL":
            factor_node = Node("STRING_LITERAL", parent=node)
            self.next_token()
            return True
        if self.BoolValue(node) or self.List(node):
            return True
        return False



    #Funcion que arma todo
    def parse(self):
        self.Program()
        if len(self.input_tokens) > 0:
            self.arbol = None
            while True:
                self.synchronize()
                if self.current_token == "$":
                    break
                self.Program()
            print("error(s): ", len(self.output_errors))
            for i in self.output_errors:
                print(i)
        else:
            print("abstract syntax tree: ")
            render_tree(self.arbol)
