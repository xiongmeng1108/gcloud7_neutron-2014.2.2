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

"""floatingip_qos

Revision ID: 2806f2233aca
Revises: 3ddd7a375d0
Create Date: 2015-12-01 17:09:47.023664

"""

# revision identifiers, used by Alembic.
revision = '2806f2233aca'
down_revision = '3ddd7a375d0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gcloudqueueqoss',
    sa.Column('create_time', sa.String(length=26), nullable=True),
    sa.Column('floating_port_id', sa.String(length=36), nullable=False),
    sa.Column('src_ip', sa.String(length=32), nullable=True),
    sa.Column('max_rate', sa.BIGINT(), nullable=True),
    sa.Column('min_rate', sa.BIGINT(), nullable=True),
    sa.ForeignKeyConstraint(['floating_port_id'], ['ports.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('floating_port_id'),
    mysql_engine='InnoDB'
    )


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('gcloudqueueqoss')
    ### end Alembic commands ###