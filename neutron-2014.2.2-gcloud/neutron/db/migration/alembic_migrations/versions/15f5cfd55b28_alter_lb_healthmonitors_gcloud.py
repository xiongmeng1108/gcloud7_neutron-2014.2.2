# Copyright 2015 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

"""alter_lb_healthmonitors_gcloud

Revision ID: 15f5cfd55b28
Revises: a71fbeac4ed
Create Date: 2015-07-14 13:49:01.468639

"""

# revision identifiers, used by Alembic.
revision = '15f5cfd55b28'
down_revision = 'a71fbeac4ed'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "healthmonitors",
         sa.Column('create_time',sa.String(length=26), nullable=True)
    )
    op.add_column(
        "healthmonitors",
         sa.Column('user_id',sa.String(length=64), nullable=True)
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(
        "healthmonitors",
        'create_time')
    op.drop_column(
        "healthmonitors",
        'user_id')
    ### end Alembic commands ###