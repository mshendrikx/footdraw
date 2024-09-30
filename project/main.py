import random

from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import and_
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from . import db

from .models import User, Player, Group, Groupadm, Draworder

class ConstValue:
    zero = 0
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5
    
class Team:
    id = 0
    defense = 0
    midfilder = 0
    forward = 0
    overall = 0

main = Blueprint("main", __name__)

@main.route("/")
def index():

    return render_template("index.html", user=current_user)

@main.route("/profile")
@login_required
def profile():

    groups = None
    
    if current_user.admin == 'X':
        groups = Group.query.all()
    
    else:
    
        groups_adm = Groupadm.query.filter_by(userid=current_user.id)
    
        groups_id = []
        for group_adm in groups_adm:
            groups_id.append(group_adm.groupid)
        
        if groups_id:
            query = db.session.query(Group)
            groups = query.filter(Group.id.in_(groups_id)).order_by(Group.name)

    return render_template("profile.html", current_user=current_user, groups=groups)


@main.route("/profile", methods=["POST"])
@login_required
def profile_post():

    password = request.form.get("password")
    repass = request.form.get("repass")
    name = request.form.get("name")
    groupid = request.form.get("group_selection")
    email = request.form.get("email")

    if password != repass:
        flash("Password está diferente")
        flash("alert-danger")
        return redirect(url_for("main.profile"))

    if '@' not in email:
        flash("Entrar E-mail válido")
        flash("alert-danger")
        return redirect(url_for("main.profile"))
            
    if password != "":
        current_user.password = generate_password_hash(password, method="pbkdf2:sha256")

    if groupid != current_user.groupid:
        current_user.groupid = groupid

    if name != "":
        current_user.name = name
        
    current_user.email = email

    db.session.add(current_user)
    db.session.commit()

    return redirect(url_for("main.profile"))

@main.route("/creategroup", methods=["POST"])
@login_required
def creategroup():

    if current_user.admin == "":
        flash("Só administradores podem criar grupos.")
        flash("alert-danger")
        return redirect(url_for("main.index"))

    # login code goes here
    group_name = request.form.get("group_name")

    try:
        new_group = Group(
            name=group_name,
        )
        db.session.add(new_group)
        db.session.commit()
        flash("Grupo criado.")
        flash("alert-success")
    except:
        flash("Não foi possível criar o grupo.")
        flash("alert-danger")

    return redirect(url_for("main.configuration"))


@main.route("/configuration")
@login_required
def configuration():

    if current_user.admin == "":
        flash("Só administradores podem configurar.")
        flash("alert-danger")
        return redirect(url_for("main.index"))

    users = User.query.order_by(User.name).all()

    groups = Group.query.order_by(Group.name).all()

    return render_template(
        "configuration.html",
        current_user=current_user,
        users=users,
        groups=groups,
    )


@main.route("/delgroup", methods=["POST"])
@login_required
def delgroup():

    if current_user.admin == "":
        flash("Deve ser admnistrador.")
        flash("alert-danger")
        return redirect(url_for("main.index"))

    # login code goes here
    groupid = request.form.get("group_delete")
    
    if groupid == "":
        flash("Selecionar grupo.")
        flash("alert-danger")
        return redirect(url_for("main.configuration"))        
    
    group = Group.query.filter_by(id=groupid).delete()

    if not group:
        flash("Grupo não existe.")
        flash("alert-danger")
    else:
        flash("Grupo apagado.")
        flash("alert-success")
        Groupadm.query.filter_by(groupid=groupid).delete()
        Player.query.filter_by(groupid=groupid).delete()
        users = User.query.filter_by(groupid=groupid).first()
        if users:
            for user in users:
                user.groupid = 0

    db.session.commit()

    return redirect(url_for("main.configuration"))


@main.route("/updateuser", methods=["POST"])
@login_required
def updateuser():

    if current_user.admin == "":
        flash("Deve ser administrador.")
        flash("alert-danger")
        return redirect(url_for("main.index"))

    userid = request.form.get("updateuserid")
    
    if userid == "":
        flash("Selecionar usuário.")
        flash("alert-danger")
        return redirect(url_for("main.configuration"))        

    if request.form["action"] == "Criar":
        new_user = User(            
                id=userid,
                name="Modificar",
                groupid=0,
                password=generate_password_hash("F00tDr4w", method="pbkdf2:sha256"),
                email="",
                admin="",
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Usuário criado.")
        flash("alert-success")
        return redirect(url_for("main.configuration"))

    user = User.query.filter_by(id=userid).first()

    if not user:
        flash("Usuário não existe.")
        flash("alert-danger")
        return redirect(url_for("main.configuration"))
        
    if request.form["action"] == "Reset":
        user.password = generate_password_hash("F00tDr4w", method="pbkdf2:sha256")
        flash("Password modificada para: F00tDr4w")
        flash("alert-success")
        
    elif request.form["action"] == "Apagar":
        if userid == current_user.id or userid == "admin":
            flash("Usuário não pode ser apagado.")
            flash("alert-success")      
        else:    
            User.query.filter_by(id=userid).delete()  
            Groupadm.query.filter_by(id=userid).delete() 
            flash("Usuário apagado.")
            flash("alert-success")
            
    elif request.form["action"] == "Admin":
        if user.admin == "X":
            flash("Administrador removido.")
            flash("alert-success")
            user.admin = ""
        else:
            flash("Administrador adicionado.")
            flash("alert-success")
            user.admin = "X"

    db.session.commit()

    return redirect(url_for("main.configuration"))

@main.route("/players")
@login_required
def players():
    
    if current_user.groupid < 1:
        flash("Primeiro selecionar grupo.")
        flash("alert-danger")
        return redirect(url_for("main.profile"))
    
    group = Group.query.filter_by(id=current_user.groupid)
    
    players_db = Player.query.filter_by(groupid=current_user.groupid).order_by(Player.checkin, Player.name)
    
    players = []
    for player_db in players_db:
        if player_db.checkin > 0:
            players.append(player_db)
    for player_db in players_db:
        if player_db.checkin == 0:
            players.append(player_db)    
            
    constvalue = ConstValue()
            
    return render_template("players.html", group=group, players=players, constvalue=constvalue)
    
@main.route("/group")
@login_required
def group():
    
    if current_user.groupid < 1:
        flash("Primeiro selecionar grupo.")
        flash("alert-danger")
        return redirect(url_for("main.profile"))   
    
    draw_orders = Draworder.query.filter_by(groupid=current_user.groupid)
    
    posorders = []
    count = 1
    for draw_order in draw_orders:
        posorder = []
        posorder.append(count)
        if draw_order.position == 1:
            position = 'Defesa'
        elif draw_order.position == 2:
            position = 'Meio-Campo'
        elif draw_order.position == 3:
            position = 'Atacante'        
        elif draw_order.position == 4:
            position = 'Overall'    
        posorder.append(position)
        posorders.append(posorder)
        count += 1
    
    group = Group.query.filter_by(id=current_user.groupid).first()
    return render_template("group.html", current_user=current_user, group=group, posorders=posorders)
    
@main.route("/editgroup", methods=["POST"])
@login_required
def editgroup():

    if current_user.groupid < 1:
        flash("Selecionar grupo.")
        flash("alert-danger")
        return redirect(url_for("main.profile"))
    
    if request.form["action"] == "Adicionar":
        position = request.form.get("position_selection")
        
        if position == "":
            flash("Selecionar posição.")
            flash("alert-danger")
            return redirect(url_for("main.group"))            

        new_draw_order = Draworder(
                groupid=int(current_user.groupid),
                position=int(position),
            )

        try:
            db.session.add(new_draw_order)
            db.session.commit()
            flash("Ordem de sorteio inserida.")
            flash("alert-success")
        except:
            flash("Falha ao inserir ordem de sorteio.")
            flash("alert-danger")      
            
    elif request.form["action"] == "Reiniciar":
        Draworder.query.filter_by(groupid=current_user.groupid).delete()
        db.session.commit()
    
    return redirect(url_for("main.group"))

@main.route("/addplayer", methods=["POST"])
@login_required
def addplayer():
    
    if request.form["action"] == "Create":
        player_name = request.form.get("add_player")
        if player_name == "":
            flash("Qual o nome do novo jogador")
            flash("alert-danger")  
        else:
            player = Player.query.filter_by(groupid=current_user.groupid, name=player_name).first()
            if player:
                flash("Já existe jogador com este nome")
                flash("alert-danger")   
            else:               
                new_player = Player(
                    name = player_name,
                    groupid = current_user.groupid,
                    defense = 0,
                    midfilder = 0,
                    forward = 0,
                    overall = 0, 
                    checkin = 0,
                    team = 0,            
                )
                db.session.add(new_player)
                db.session.commit()
                
                player = Player.query.filter_by(groupid=current_user.groupid, name=player_name).first()
                
                if player:
                    return redirect(url_for("main.editplayer", playerid=player.id))
        
    elif request.form["action"] == "Clear":
        players = Player.query.filter_by(groupid=current_user.groupid)
        for player in players:
            player.checkin = 0
        db.session.commit()
        
    return redirect(url_for("main.players"))

@main.route("/editplayer/<playerid>")
@login_required
def editplayer(playerid):
    
    player = Player.query.filter_by(id=playerid).first()
    
    constvalue = ConstValue()
    return render_template("player.html", player=player, constvalue=constvalue)
   
@main.route("/checkin/<playerid>")
@login_required
def checkin(playerid):

    players = Player.query.filter_by(groupid=current_user.groupid)
    last_checkin = 0
    for player in players:
        if player.checkin > last_checkin:
            last_checkin = player.checkin
    
    player = Player.query.filter_by(id=playerid).first()
    
    player.checkin = last_checkin + 1
    
    db.session.commit()    
    
    return redirect(url_for("main.players"))   
        
    
@main.route("/checkout/<playerid>")
@login_required
def checkout(playerid):
    
    player = Player.query.filter_by(id=playerid).first()    
    player_checkin = player.checkin
    
    players_db = Player.query.filter_by(groupid=current_user.groupid)
    
    for player_db in players_db:
        if player_db.checkin > player_checkin:
            player_db.checkin -= 1
        elif player_db.checkin == player_checkin:
            player_db.checkin = 0           
    
    db.session.commit()    
    
    return redirect(url_for("main.players"))   

@main.route("/updateskill/<playerid>/<skillid>/<skillvalue>")
@login_required
def updateskill(playerid, skillid, skillvalue):
    
    player = Player.query.filter_by(id=playerid).first()    
    
    if skillid == '1':
        player.defense = int(skillvalue)
    elif skillid == '2':
        player.midfilder = int(skillvalue)
    else:
        player.forward = int(skillvalue)
        
    player.overall = ((player.defense + player.midfilder + player.forward) * 20) / 3
        
    db.session.commit()   
    
    return redirect(url_for("main.editplayer", playerid=player.id)) 

@main.route("/linkuser", methods=["POST"])
@login_required
def linkuser():
    
    groupid = int(request.form.get("group_sel"))    
    userid = request.form.get("updateuserid")
    
    if groupid == "":
        flash("Selecionar grupo.")
        flash("alert-danger")   

    groupadm = Groupadm.query.filter_by(groupid=groupid, userid=userid).first()
    
    if groupadm:
        groupadm_del = Groupadm.query.filter_by(groupid=groupid, userid=userid).delete()
    else:
        new_groupadm = Groupadm(
            groupid = groupid,
            userid = userid,
        )
        db.session.add(new_groupadm)
        
    db.session.commit()  
    
    return redirect(url_for("main.configuration"))

@main.route("/teams")
@login_required
def teams():
    
    if current_user.groupid < 1:
        flash("Primeiro selecionar grupo.")
        flash("alert-danger")
        return redirect(url_for("main.profile"))
    
    players_per_team = int(Draworder.query.filter_by(groupid=current_user.groupid).count())
    
    if players_per_team == 0:
        flash("Configurar grupo.")
        flash("alert-danger")
        return redirect(url_for("main.group"))       
    
    players = Player.query.filter_by(groupid=current_user.groupid).order_by(Player.team, Player.name)
    
    teams = []
    defense_array = []
    midfielder_array  = []
    forward_array  = []
    overall_array  = []
    teams_players = []
    
    for player in players:
        if player.team > 0:
            teams_players.append(player)
            if not player.team in teams:
                teams.append(player.team)
                defense_array.append(player.defense)
                midfielder_array.append(player.midfilder)
                forward_array.append(player.forward)
                overall_array.append(player.overall)
            else:
                team_index = teams.index(player.team)
                defense_array[team_index] += player.defense
                midfielder_array[team_index] += player.midfilder
                forward_array[team_index] += player.forward
                overall_array[team_index] += player.overall
    
    teams_array = []
    team_index = 0
    for team in teams:
        team_class = Team()
        team_class.id = team
        team_class.defense = int(defense_array[team_index] * 20 / players_per_team)
        team_class.midfilder = int(midfielder_array[team_index] * 20 / players_per_team)
        team_class.forward = int(forward_array[team_index] * 20 / players_per_team)
        team_class.overall = int(overall_array[team_index] / players_per_team)
        teams_array.append(team_class)
        team_index += 1
        
    group = Group.query.filter_by(id=current_user.groupid).first()
        
    return render_template("teams.html", teams=teams_array, players=teams_players, group=group)
   
@main.route("/editteams", methods=["POST"])
@login_required
def editteams():
    
    if current_user.groupid < 1:
        flash("Primeiro selecionar grupo.")
        flash("alert-danger")
        return redirect(url_for("main.profile"))
    
    draw_order = Draworder.query.filter_by(groupid=current_user.groupid)
    
    players_per_team = int(draw_order.count())
    
    if players_per_team == 0:
        flash("Configurar grupo.")
        flash("alert-danger")
        return redirect(url_for("main.group"))      
    
    if request.form["action"] == "Apagar":
        try:
            players = Player.query.filter_by(groupid=current_user.groupid)
            players.update({Player.team: 0}, synchronize_session=False)
            db.session.commit()
        except:
            1 == 1
    else:
        min_players = players_per_team * 2
        players = Player.query.filter(getattr(Player, "checkin") > 0, getattr(Player, "groupid") == current_user.groupid)
        checked_players = int(players.count())
        if checked_players < min_players:
            message = "São necessários pelo menos " + str(min_players) + " jogadores para criar os times"
            flash(message)
            flash("alert-danger")
        else:
            total_teams = checked_players // players_per_team
            count = 1            
            teams = []
            while count <= total_teams:
                team = []
                team.append(count)
                team.append(0)
                team.append(0)
                team.append(0)
                team.append(0)
                teams.append(team) 
                count += 1
                
            max_players = total_teams * players_per_team
            
            players = players.filter(getattr(Player, "checkin") <= max_players, getattr(Player, "groupid") == current_user.groupid)
            
            for player in players:
                player.random = random.randint(1, 99999)
            db.session.commit() 
            
            for position_order in draw_order:
                if position_order.position == 1:
                    teams.sort(key=lambda x: (x[1], x[4]))
                elif position_order.position == 2:
                    teams.sort(key=lambda x: (x[2], x[4]))
                elif position_order.position == 3:
                    teams.sort(key=lambda x: (x[3], x[4]))
                else:
                    teams.sort(key=lambda x: (x[4]))
                    players = players.order_by(Player.overall.desc())                    
                
                for team in teams:
                    if position_order.position == 1:
                        player = players.order_by(Player.defense.desc(), Player.overall.desc(), Player.random).first()
                    elif position_order.position == 2:
                        player = players.order_by(Player.midfilder.desc(), Player.overall.desc(), Player.random).first()
                    elif position_order.position == 3:
                        player = players.order_by(Player.forward.desc(), Player.overall.desc(), Player.random).first()
                    else:
                        player = players.order_by(Player.overall.desc(), Player.random).first()                    

                    player.team = team[0]
                    db.session.commit() 
                    team[1] += player.defense
                    team[2] += player.midfilder
                    team[3] += player.forward
                    team[4] += player.overall
                    players = players.filter(getattr(Player, "id") != player.id)              
    
    return redirect(url_for("main.teams"))

@main.route("/delplayer/<playerid>")
@login_required
def delplayer(playerid):
        
    player = Player.query.filter_by(id=playerid).delete()
    db.session.commit() 
    flash("Jogador apagado.")
    flash("alert-success")
    return redirect(url_for("main.players"))        

@main.route("/order")
@login_required
def order():
    
    if current_user.groupid < 1:
        flash("Primeiro selecionar grupo.")
        flash("alert-danger")
        return redirect(url_for("main.profile"))
    
    group = Group.query.filter_by(id=current_user.groupid).first()
    
    players = Player.query.filter(getattr(Player, "checkin") > 0, getattr(Player, "groupid") == current_user.groupid)
    
    for player in players:
        player.random = random.randint(1, 99999)
    
    db.session.commit()
    
    players = players.order_by(Player.random)
    
    count = 1
    for player in players:
        player.random = count
        count += 1
    
    db.session.commit()
    
    return render_template("order.html", players=players, group=group)