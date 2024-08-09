import React from 'react'

function NoDataInfo(props) {
    const {dataName} = props;
    return (
        <div className='alert alert-info mt-2 text-center'>
            {`There aren't ${dataName} yet.`}
        </div>
    )
}

export default NoDataInfo