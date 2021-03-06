# -*- coding: utf-8 -*-
from sqlalchemy import Table, Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.sql import func
from sqlalchemy.types import Date, Enum, DateTime
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
from demokratikollen.core.utils import misc as misc_utils, postgres as pg_utils


from flask.ext.jsontools import JsonSerializableBase

Base = declarative_base(cls=(JsonSerializableBase,))

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    intressent_id = Column(String(250))
    first_name = Column(String(250))
    last_name = Column(String(250))
    birth_year = Column(Integer)
    gender = Column(String(10))
    image_url_md = Column(String(250))
    image_url_sm = Column(String(250))
    image_url_lg = Column(String(250))
    url_name = Column(String(250))
    party_id = Column(Integer, ForeignKey('groups.id'))
    votes = relationship('Vote', backref='member')
    appointments = relationship('Appointment', backref='member')
    current_group_appointments = relationship("GroupAppointment",
                    primaryjoin="and_(Member.id==GroupAppointment.member_id,"
                                    "GroupAppointment.start_date<=func.now(),"
                                    "GroupAppointment.end_date>=func.now())")

    def __repr__(self):
        return '{}, {} ({})'.format(self.last_name,self.first_name,self.party.abbr)


#########################
# Appointments
#########################

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    start_date = Column(Date)
    end_date = Column(Date)
    classtype = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'appointment',
        'polymorphic_on':classtype
    }

class SpeakerAppointment(Appointment):
    position =  Column(Enum('Talman','Förste vice talman','Andre vice talman','Tredje vice talman',name='speaker_positions'))

    __mapper_args__ = {
        'polymorphic_identity':'speaker_appointment'
    }

class ChamberAppointment(Appointment):
    __tablename__ = 'chamber_appointments'
    id = Column(Integer,ForeignKey('appointments.id'),primary_key=True)
    status = Column(Enum('Ledig','Tjänstgörande',name='chamber_appointment_statuses'))
    role = Column(Enum('Riksdagsledamot','Ersättare',name='chamber_appointment_roles'))
    chair = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity':'chamber_appointment'
    }

    def title(self):
        return '{} {} {}'.format(self.status,self.role,self.member)
    def __repr__(self):
        return 'Chair {}: {} {} {}-{}: {}'.format(self.chair,self.status,self.role,self.start_date,self.end_date,self.member)


class GroupAppointment(Appointment):
    __tablename__ = 'group_appointments'
    id = Column(Integer,ForeignKey('appointments.id'),primary_key=True)
    role = Column(String(250))
    group_id = Column(Integer, ForeignKey('groups.id'))

    __mapper_args__ = {
        'polymorphic_identity':'group_appointment'
    }

class CommitteeAppointment(GroupAppointment):

    __mapper_args__ = {
        'polymorphic_identity':'committee_appointment'
    }

class MinistryAppointment(GroupAppointment):

    __mapper_args__ = {
        'polymorphic_identity':'ministry_appointment'
    }

#########################
# Groups
#########################

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    abbr = Column(String(100))
    appointments = relationship('GroupAppointment', backref='group')
    classtype = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'group',
        'polymorphic_on':classtype
    }


class Committee(Group):
    reports = relationship('CommitteeReport', backref='committee')

    __mapper_args__ = {
        'polymorphic_identity':'committee'
    }


class Ministry(Group):
    proposals = relationship('GovernmentProposal', primaryjoin="Ministry.id==GovernmentProposal.ministry_id")

    __mapper_args__ = {
        'polymorphic_identity':'ministry'
    }


class Party(Group):
    members = relationship('Member', backref='party')

    __mapper_args__ = {
        'polymorphic_identity':'party',
    }
    def __repr__(self):
        return 'Party {}: {} ({})'.format(self.id,self.name,self.abbr)

#########################
# Voting
#########################

VoteOptionsType = Enum('Ja','Nej','Avstår','Frånvarande',name='vote_options')

class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    polled_point_id = Column(Integer, ForeignKey('committee_report_points.id'))
    vote_option = Column(VoteOptionsType)

    def __repr__(self):
        return '{}: {}'.format(self.member.__repr__(),self.vote_option.__repr__())


#########################
# Documents
#########################

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    dok_id = Column(String(100))
    published = Column(DateTime)
    session = Column(String(10))
    code = Column(String(20))
    title = Column(String(250))
    classtype = Column(String(50))
    text_url = Column(String(250))

    __mapper_args__ = {
        'polymorphic_identity':'document',
        'polymorphic_on':classtype
    }

    def unique_code(self):
        return "{}:{}".format(self.session,self.code)

    def __repr__(self):
        return '{}-{}: {}'.format(self.session, self.dok_id, self.title)
    
class CommitteeReport(Document):
    __tablename__ = 'committee_reports'
    id = Column(Integer, ForeignKey('documents.id'), primary_key=True)
    committee_id = Column(Integer, ForeignKey('groups.id'))
    points = relationship('CommitteeReportPoint', backref='report')
    proposal_points = relationship('ProposalPoint',primaryjoin='CommitteeReport.id==ProposalPoint.committee_report_id')

    __mapper_args__ = {
        'polymorphic_identity':'committee_report',
    }

class CommitteeReportPoint(Base):
    __tablename__ = 'committee_report_points'
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    title = Column(String(250))
    committee_report_id = Column(Integer, ForeignKey('committee_reports.id'))
    classtype = Column(String(50))

    __mapper_args__ = {
        'polymorphic_on':classtype,
        'polymorphic_identity':'committee_report_point'
    }

class AcclaimedPoint(CommitteeReportPoint):

    __mapper_args__ = {
        'polymorphic_identity':'acclaimed_point'
    }

class PolledPoint(CommitteeReportPoint):
    poll_date = Column(Date)
    votes = relationship('Vote', backref='polled_point')
    r_votering_id = Column(String(250))

    __mapper_args__ = {
        'polymorphic_identity':'polled_point'
    }


#########################
# Proposals
#########################

decision_outcomes = Enum('Avslag','Bifall','Delvis bifall','-',name='decision_outcomes')

class Proposal(Document):
    __tablename__ = 'proposals'
    id = Column(Integer, ForeignKey('documents.id'), primary_key=True)
    points = relationship('ProposalPoint',backref='proposal')

    __mapper_args__ = {
        'polymorphic_identity':'proposal'
    }

class ProposalPoint(Base):
    __tablename__ = 'proposal_points'
    id = Column(Integer, primary_key=True)
    number = Column(Integer)

    proposal_id = Column(Integer, ForeignKey('proposals.id'))
    committee_report_id = Column(Integer,ForeignKey('committee_reports.id'))
    committee_report = relationship('CommitteeReport',foreign_keys="[ProposalPoint.committee_report_id]")
    committee_recommendation = Column(decision_outcomes)
    decision = Column(decision_outcomes)


# Association table needed for many-to-many relationships (members-proposals)
association_member_proposal = Table('association_member_proposal', Base.metadata,
    Column('member_id', Integer, ForeignKey('members.id')),
    Column('member_proposal_id', Integer, ForeignKey('proposals.id'))
)

MemberProposalTypes = Enum('Enskild motion','Kommittémotion','Följdmotion',
                            'Partimotion','Flerpartimotion','Fristående motion','-',
                            name='member_proposal_types')

class MemberProposal(Proposal):
    subtype = Column(MemberProposalTypes)
    signatories = relationship('Member',
                                secondary=association_member_proposal,
                                backref='proposals')

    __mapper_args__ = {
        'polymorphic_identity':'member_proposal'
    }

class GovernmentProposal(Proposal):
    ministry_id = Column(Integer, ForeignKey('groups.id'))
    ministry = relationship('Ministry',foreign_keys="[GovernmentProposal.ministry_id]")

    __mapper_args__ = {
        'polymorphic_identity':'government_proposal'
    }


#########################
# Calculated data
#########################

class PartyVote(Base):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        nyes = kwargs['num_yes']
        nno = kwargs['num_no']
        nabstain = kwargs['num_abstain']
        if nyes > nno and nyes > nabstain:
            self.vote_option = 'Ja'
        elif nno > nyes and nno > nabstain:
            self.vote_option = 'Nej'
        elif nabstain > nno and nabstain > nyes:
            self.vote_option = 'Avstår'
        else:
            self.vote_option = 'Frånvarande'

    __tablename__ = 'party_votes'
    id = Column(Integer, primary_key=True)
    party_id = Column(Integer, ForeignKey('groups.id'))
    polled_point_id = Column(Integer, ForeignKey('committee_report_points.id'))
    num_yes = Column(Integer)
    num_no = Column(Integer)
    num_abstain = Column(Integer)
    num_absent = Column(Integer)
    vote_option = Column(VoteOptionsType)

    def __repr__(self):
        return '{}: {}'.format(self.member.__repr__(),self.vote_option.__repr__())


def create_db_structure(engine, do_not_confirm=False):
    if do_not_confirm or misc_utils.yes_or_no("Do you really want to drop everything in the database?"):
        pg_utils.drop_everything(engine)

    Base.metadata.create_all(engine)

if __name__ == '__main__':
    pass

